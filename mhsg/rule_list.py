# -*- coding: utf-8 -*-

import importlib
import importlib.util
import inspect
import os
import pkgutil
import sys

from mhsg import exceptions, language
from mhsg.rules import package_scope

from . import config, deprecated_rule, junit, report, severity, utils

NUMBER_OF_SUBPHASES = 7


def get_python_modules_from_directory(sDirectoryName, lModules):
    """
    Returns a list of files with an extension of py from a directory.
    It ignores files starting with a double underscore __.

    Parameters:

      sDirectoryName (string)

    Modifies:

      lModules (string list)
    """
    lDirectoryContents = os.listdir(sDirectoryName)
    for sFileName in lDirectoryContents:
        if sFileName.endswith(".py") and not sFileName.startswith("__"):
            lModules.append(sFileName.replace(".py", ""))


def get_rules_from_module(lModules, lRules):
    """
    Returns a list of files that start with "rule_".

    Parameters:

      lModules (list)

    Modifies:

      lRules (object list)
    """
    for sModuleName in lModules:
        for name, obj in inspect.getmembers(importlib.import_module(sModuleName)):
            if name.startswith("rule_") and name != "rule_item":
                lRules.append(obj())


def load_local_rules(sDirectoryName, iDirectory=0):
    """
    Loads rules from the directory passed to this routine.

    Modules are loaded from their file path with a name unique to the directory,
    so rule files with the same name in different directories do not collide.

    Parameters:

      sDirectoryName (string)

      iDirectory (integer)

    Returns: (string list)
    """
    lLocalModules = []
    get_python_modules_from_directory(sDirectoryName, lLocalModules)
    lRules = []
    for sModuleName in lLocalModules:
        sUniqueName = f"mhsg_local_rules_{iDirectory}_{sModuleName}"
        oSpec = importlib.util.spec_from_file_location(sUniqueName, os.path.join(sDirectoryName, sModuleName + ".py"))
        oModule = importlib.util.module_from_spec(oSpec)
        sys.modules[sUniqueName] = oModule
        oSpec.loader.exec_module(oModule)
        for name, obj in inspect.getmembers(oModule):
            if name.startswith("rule_") and name != "rule_item":
                lRules.append(obj())
    return lRules


def load_rules():
    """
    Loads rules from the mhsg/rules directory.

    Parameters:  None

    Returns:  (rule object list)
    """
    lRules = []
    oRules = importlib.import_module("mhsg.rules")
    # Each rule group is a package in mhsg/rules
    lPackageNames = sorted(oModule.name for oModule in pkgutil.iter_modules(oRules.__path__) if oModule.ispkg)
    for sPackageName in lPackageNames:
        oPackage = importlib.import_module("mhsg.rules." + sPackageName)
        for rule_name, oRule in inspect.getmembers(oPackage, inspect.isclass):
            if rule_name.startswith("rule_"):
                lRules.append(oRule())
    return lRules


def maximum_phase(lRules):
    """
    Determines the maximum phase number from all the rules.

    Parameters:
      lRules (rule object list)

    Returns: (integer)
    """
    maximumPhaseNumber = 0
    for oRule in lRules:
        if oRule.phase > maximumPhaseNumber:
            maximumPhaseNumber = oRule.phase
    return maximumPhaseNumber


class rule_list:
    """
    Contains a list of all rules to be checked.
    It loads all base rules.
    Localized rules are loaded if specified.

    Parameters:

      oVhdlFile: (vhdlFile object)

      oSeverityList: (severity list object)

      sLocalRulesDirectory: (string) (optional)
    """

    def __init__(self, oVhdlFile, oSeverityList, sLocalRulesDirectory=None, bAllLanguages=False):
        self.rules = load_rules()
        for iDirectory, sDirectory in enumerate(config.get_local_rule_directories(sLocalRulesDirectory)):
            self.rules.extend(load_local_rules(sDirectory, iDirectory))
        # Only the rules for the language of the file, unless the rules of every language are listed, as for -oc and -rc
        if not bAllLanguages:
            sLanguageName = getattr(oVhdlFile, "language", language.VHDL)
            self.rules = [o for o in self.rules if sLanguageName in getattr(o, "languages", (language.VHDL,))]
        self.iNumberRulesRan = 0
        self.lastPhaseRan = 0
        self.oVhdlFile = oVhdlFile
        self.maximumPhase = maximum_phase(self.rules)
        self.violations = False
        self.had_violations = False
        self.oSeverityList = oSeverityList

    def fix(self, iFixPhase=7, lSkipPhase=None, dFixOnly=None):
        """
        Applies fixes to all violations found.

        Parameters:

          iFixPhase : (integer)

          lSkipPhases : (list of integers)

          dFixOnly : (fix list dictionary)
        """
        if lSkipPhase is None:
            lSkipPhase = []
        for phase in range(1, int(iFixPhase) + 1):
            if phase in lSkipPhase:
                if phase == 1:
                    self.oVhdlFile.set_token_indent()
                continue

            # Update indents before checking indent
            if phase == 4:
                self.oVhdlFile.set_token_indent()

            for subphase in range(0, NUMBER_OF_SUBPHASES):
                lRules = self.get_rules_in_phase(phase)
                lRules = self.get_rules_in_subphase(lRules, subphase, bFix=True)
                lRules = filter_out_disabled_rules(lRules)
                lRules = enforce_prerequisites(lRules)
                for oRule in lRules:
                    # print(oRule.unique_id)
                    if oRule.severity.type == severity.error_type:
                        oRule.fix(self.oVhdlFile, dFixOnly)
                        if oRule.had_violations:
                            self.had_violations = True
                    else:
                        oRule.analyze(self.oVhdlFile)

            if phase == 1:
                self.oVhdlFile.fix_blank_lines()
                self.oVhdlFile.fix_trailing_whitespace()
                self.oVhdlFile.update_token_map()

    def get_rules_in_phase(self, iPhaseNumber):
        """
        Returns a list of rules in a given phase.

        Parameters:

          iPhaseNumber : (integer)

        Returns: (list of rule objects)
        """
        lReturn = []
        for oRule in self.rules:
            if oRule.phase == iPhaseNumber and not oRule.lint:
                lReturn.append(oRule)
        return lReturn

    def check_lint_rules(self):
        """
        Analyzes the enabled lint rules and returns the number of error violations.
        Lint rules run before the phases and do not stop a run, so their results do not depend on formatting.
        """
        iFailures = 0
        for oRule in filter_out_disabled_rules([o for o in self.rules if o.lint]):
            oRule.analyze(self.oVhdlFile)
            if oRule.get_report_severity().type == severity.error_type:
                iFailures += len(oRule.violations)
            self.iNumberRulesRan += 1
        return iFailures

    def get_rules_in_subphase(self, lRules, iSubPhase, bFix=False):
        """
        Returns a list of rules in a given subphase.

        Parameters:

          lRules : (list of rule objects)

          iSubPhase : (integer)

          bFix : (boolean) also return the rules whose fix runs again in this subphase

        Returns: (list of rule objects)
        """
        lReturn = []
        for oRule in lRules:
            if oRule.subphase == iSubPhase:
                lReturn.append(oRule)
            elif bFix and oRule.fix_again_in_subphase == iSubPhase:
                lReturn.append(oRule)
        return lReturn

    def check_rules(self, bAllPhases=False, lSkipPhase=None):
        """
        Analyzes all rules in increasing phase order.
        If there is a violation in a phase, analysis is halted.

        Parameters:

            bAllPhases : (boolean)
            lSkipPhase : (list of integers)
        """
        if lSkipPhase is None:
            lSkipPhase = []
        self.iNumberRulesRan = 0
        self.violations = False
        iFailures = self.check_lint_rules()
        for phase in range(1, 8):
            if phase in lSkipPhase:
                continue

            for subphase in range(0, NUMBER_OF_SUBPHASES):
                lRules = self.get_rules_in_phase(phase)
                lRules = self.get_rules_in_subphase(lRules, subphase)
                lRules = filter_out_disabled_rules(lRules)

                for oRule in lRules:
                    oRule.analyze(self.oVhdlFile)
                    if oRule.get_report_severity().type == severity.error_type:
                        iFailures += len(oRule.violations)
                    self.iNumberRulesRan += 1
                self.lastPhaseRan = phase
                if iFailures > 0:
                    self.violations = True
            if self.violations:
                if not bAllPhases:
                    break

    def report_violations(self, sOutputFormat):
        """
        Prints out violations to stdout.

        Parameters:

          sOutputFormat (string)
        """
        dRunInfo = {}
        dRunInfo["filename"] = self.oVhdlFile.filename
        dRunInfo["stopPhase"] = 7
        dRunInfo["violations"] = []

        for oRule in self.rules:
            if oRule.has_violations():
                lViolations = oRule.get_violations()
                dRunInfo["violations"].extend(lViolations)
        dRunInfo["violations"] = sorted(dRunInfo["violations"], key=lambda x: int(x["lineNumber"]))
        dRunInfo["stopPhase"] = self.lastPhaseRan
        dRunInfo["num_rules_checked"] = self.get_number_of_rules_ran()
        dRunInfo["total_violations"] = len(dRunInfo["violations"])
        dRunInfo["maxSeverityNameLength"] = self.oSeverityList.iMaxNameLength
        dRunInfo["severities"] = {}

        for oSeverity in self.oSeverityList.get_severities():
            dRunInfo["severities"][oSeverity.name] = 0
        for dViolation in dRunInfo["violations"]:
            name = dViolation["severity"]["name"]
            dRunInfo["severities"][name] = dRunInfo["severities"][name] + 1

        if sOutputFormat == "mhsg":
            sOutputStd, sOutputErr = report.mhsg_stdout.print_output(dRunInfo)
        elif sOutputFormat == "syntastic":
            sOutputStd, sOutputErr = report.syntastic_stdout.print_output(dRunInfo)
        else:
            sOutputStd, sOutputErr = report.summary_stdout.print_output(dRunInfo)
        return sOutputStd, sOutputErr

    def configure(self, oConfig):
        """
        Configures individual rules based on dictionary passed.

        Parameters:

          configurationFile: (dictionary)
        """
        lDeprecatedMessages = []
        configurationFile = oConfig.dConfig
        if configurationFile and "rule" in configurationFile:
            self._validate_configuration_rule_exists(configurationFile)
            for oRule in self.rules:
                lDeprecatedMessages.extend(oRule.configure(oConfig))

        self._apply_package_scope()

        if len(lDeprecatedMessages) != 0:
            sErrorMessage = f"ERROR: Invalid configuration of file {self.oVhdlFile.filename}" + "\n"
            for sMessage in lDeprecatedMessages:
                sErrorMessage += sMessage + "\n"
            raise exceptions.ConfigurationError(sErrorMessage)

        try:
            if configurationFile["debug"]:
                for oRule in self.rules:
                    oRule.set_debug()
        except KeyError:
            pass

    def _apply_package_scope(self):
        """
        When a rule checking names in packages is enabled, the general rule it complements skips names in packages.
        """
        dRules = {oRule.unique_id: oRule for oRule in self.rules}
        for oRule in self.rules:
            sGeneralRule = getattr(oRule, "general_rule", None)
            if sGeneralRule in dRules:
                if oRule.disable:
                    dRules[sGeneralRule].package_scope = package_scope.ALL
                else:
                    dRules[sGeneralRule].package_scope = package_scope.EXCLUDE_PACKAGES

    def _validate_configuration_rule_exists(self, configurationFile):
        """
        Validates rules called out in the configuration files exist in the rule set.

        If a rule does not exist then:

          1) an error message will be printed
          2) tool will exit with a status of 1

        Parameters:

          configurationFile: (dictionary)

        Returns:  nothing
        """
        lRuleNames = self.get_list_of_rule_names()
        for sRule in configurationFile["rule"]:
            if rule_does_not_exist_in_list(sRule, lRuleNames):
                sErrorMessage = "ERROR: Rule " + sRule + " referenced in configuration could not be found"
                raise exceptions.ConfigurationError(sErrorMessage)

    def get_list_of_rule_names(self):
        lReturn = []
        for oRule in self.rules:
            lReturn.append(oRule.get_unique_id())
        return lReturn

    def extract_junit_testcase(self, sVhdlFileName):
        """
        Creates JUnit XML file listing all violations found.

        Parameters:

          sVhdlFileName (string)

        Returns: (junit testcase object)
        """
        oTestcase = junit.testcase(sVhdlFileName, str(0))
        oFailure = junit.failure("Failure")
        for oRule in self.rules:
            if len(oRule.violations) > 0 and oRule.get_report_severity().type == severity.error_type:
                for dViolation in oRule.violations:
                    sLine = oRule.get_display_id() + ": "
                    sLine += str(utils.get_violation_line_number(dViolation)) + " : "
                    sLine += dViolation.get_solution()
                    oFailure.add_text(sLine)

        if oFailure.has_text():
            oTestcase.add_failure(oFailure)

        return oTestcase

    def extract_violation_dictionary(self):
        """
        Creates a dictionary of violations which were found.

        Returns: (dictionary)
        """
        dReturn = {}
        dReturn["violations"] = []
        for oRule in self.rules:
            if oRule.has_violations:
                for oViolation in oRule.violations:
                    dTemp = {}
                    dTemp["rule"] = oRule.unique_id
                    if oRule.rule_set_labels:
                        dTemp["checks"] = list(oRule.rule_set_labels)
                    dTemp["linenumber"] = oViolation.get_line_number()
                    dTemp["severity"] = oRule.get_report_severity().name
                    dTemp["solution"] = oViolation.get_solution()
                    dReturn["violations"].append(dTemp)
        return dReturn

    def get_configuration(self):
        """
        Returns a dictionary with every rule and how it is configured.

        Parameters:

          None

        Returns: (dictionary)
        """
        dConfiguration = {}
        for oRule in self.rules:
            if is_rule_deprecated(oRule):
                continue
            dConfiguration[oRule.unique_id] = oRule.get_configuration()
        return dConfiguration

    def clear_violations(self):
        for oRule in self.rules:
            oRule.clear_violations()

    def get_number_of_rules_ran(self):
        return self.iNumberRulesRan


def filter_out_disabled_rules(lRules):
    """
    Removes rules which are disabled from a list of rule objects.

    Parameters:

      lRules : (list of rule objects)

    Returns: (list of rule objects)
    """
    lReturn = []
    for oRule in lRules:
        if not oRule.disable:
            lReturn.append(oRule)
    return lReturn


def is_rule_deprecated(oRule):
    if isinstance(oRule, deprecated_rule.Rule):
        return True
    return False


def rule_does_not_exist_in_list(sRule, lRuleNames):
    if is_global_configuration(sRule):
        return False
    if is_group_configuration(sRule):
        return False
    if sRule not in lRuleNames:
        return True
    return False


def is_global_configuration(sName):
    if sName == "global":
        return True
    return False


def is_group_configuration(sName):
    if sName == "group":
        return True
    return False


def enforce_prerequisites(lRules):
    lReturn = []
    lPrereqs = []
    for oRule in lRules:
        if oRule.prerequisites == []:
            lReturn.append(oRule)
        else:
            lPrereqs.append(oRule)
    lReturn.extend(lPrereqs)
    return lReturn


def rule_prerequisites_met(oRule, lTestsRan):
    print(oRule.unique_id)
    if len(oRule.prerequisites) == 0:
        return True
    for oPrerequisite in oRule.prerequisites:
        if oPrerequisite.unique_id in lTestsRan:
            return True
    return False


def get_rule_alias(oRules, sRuleId):
    for oRule in oRules.rules:
        if oRule.unique_id == sRuleId:
            return oRule.alias
    return None
