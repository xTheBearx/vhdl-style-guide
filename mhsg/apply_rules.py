# -*- coding: utf-8 -*-

import os
import shutil

from . import config, junit, rule_list, vhdlFile
from .exceptions import ClassifyError, ConfigurationError


def create_backup_file(sFileName):
    """Copies existing file and adds .bak to the end."""
    shutil.copy2(sFileName, sFileName + ".bak")


def configure_rules(oConfig, oRules, configuration, iIndex, sFileName):
    sFileName = sFileName.replace(os.sep, "/")

    configure_rules_per_rule_option(oConfig, oRules)
    configure_rules_per_file_list_option(oRules, configuration, iIndex, sFileName)
    configure_rules_per_file_rules_option(oRules, configuration, iIndex, sFileName)


def configure_rules_per_rule_option(oConfig, oRules):
    oRules.configure(oConfig)


def configure_rules_per_file_list_option(oRules, configuration, iIndex, sFileName):
    configure_rules_per_option(oRules, configuration, iIndex, sFileName, "file_list")


def configure_rules_per_file_rules_option(oRules, configuration, iIndex, sFileName):
    configure_rules_per_option(oRules, configuration, iIndex, sFileName, "file_rules")


def configure_rules_per_option(oRules, configuration, iIndex, sFileName, section):
    for dRuleConfiguration in get_rule_configurations_for_file(configuration, section, sFileName):
        oRuleConfig = config.config()
        oRuleConfig.dConfig = dRuleConfiguration
        oRules.configure(oRuleConfig)


def get_rule_configurations_for_file(configuration, section, sFileName):
    """
    Returns the rule configurations, in order, of every entry in the section which names the file.
    Paths are compared after normalization, so ./a.vhd, a.vhd and the absolute path all match.
    """
    lReturn = []
    sPath = normalize_path(sFileName)
    for dEntry in configuration.get(section, []):
        if not isinstance(dEntry, dict):
            continue
        for sEntryFileName, dRuleConfiguration in dEntry.items():
            if dRuleConfiguration is not None and normalize_path(sEntryFileName) == sPath:
                lReturn.append(dRuleConfiguration)
    return lReturn


def normalize_path(sFileName):
    return os.path.normcase(os.path.abspath(sFileName)).replace(os.sep, "/")


bStopProcessingFiles = True
bKeepProcessingFiles = False


# This function is in a separate module from __main__ as a workaround for https://bugs.python.org/issue25053
# see also https://stackoverflow.com/questions/41385708/multiprocessing-example-giving-attributeerror/42383397#42383397
def apply_rules(commandLineArguments, oConfig, tIndexFileName):
    configuration = oConfig.dConfig

    dIndent = oConfig.dIndent
    fix_only = oConfig.dFixOnly

    iIndex, sFileName = tIndexFileName
    dJsonEntry = {}
    lFileContent, eError, sEncoding = vhdlFile.utils.read_vhdlfile(sFileName, True)
    try:
        oVhdlFile = vhdlFile.vhdlFile(lFileContent, commandLineArguments, sFileName, eError, oConfig, sEncoding)
    except ClassifyError as e:
        fExitStatus = True
        testCase = create_junit_testcase(sFileName, e)
        dJsonEntry["file_path"] = sFileName
        dJsonEntry["violations"] = []
        sOutputStd = ""
        sOutputErr = f"Error while processing {sFileName}: {e.message}"
        return fExitStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bKeepProcessingFiles

    oVhdlFile.set_indent_map(dIndent)
    try:
        oRules = rule_list.rule_list(oVhdlFile, oConfig.severity_list, commandLineArguments.local_rules)
    except OSError as e:
        sOutputStd = (
            f"ERROR: encountered {e.__class__.__name__}, No such file or directory "
            + ", ".join(config.get_local_rule_directories(commandLineArguments.local_rules))
            + " when trying to open local rules file."
        )
        sOutputErr = None
        return 1, None, dJsonEntry, sOutputStd, sOutputErr, bStopProcessingFiles

    try:
        configure_rules(oConfig, oRules, configuration, iIndex, sFileName)
    except ConfigurationError as e:
        fExitStatus = True
        testCase = None
        dJsonEntry["file_path"] = sFileName
        dJsonEntry["violations"] = []
        sOutputStd = ""
        sOutputErr = f"Error while processing {sFileName}: {e.message}"
        return fExitStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bStopProcessingFiles

    if commandLineArguments.fix:
        if commandLineArguments.backup:
            create_backup_file(sFileName)
        oRules.fix(commandLineArguments.fix_phase, commandLineArguments.skip_phase, fix_only)

        if commandLineArguments.stdout:
            pass
        elif oRules.had_violations:
            write_vhdl_file(oVhdlFile, oConfig.dConfig)

    oRules.clear_violations()
    oRules.check_rules(
        bAllPhases=commandLineArguments.all_phases,
        lSkipPhase=commandLineArguments.skip_phase,
    )
    sOutputStd, sOutputErr = oRules.report_violations(commandLineArguments.output_format)
    fExitStatus = oRules.violations

    if commandLineArguments.fix and commandLineArguments.stdout:
        # The fixed code is the only output on stdout, so editors can use it as a formatter
        sOutputErr = "\n".join([sOutput for sOutput in [sOutputStd, sOutputErr] if sOutput])
        sOutputStd = get_fixed_code(oVhdlFile, oConfig.dConfig)
        fExitStatus = False

    if commandLineArguments.junit:
        testCase = oRules.extract_junit_testcase(sFileName)
    else:
        testCase = None

    if commandLineArguments.json or commandLineArguments.quality_report:
        dJsonEntry["file_path"] = sFileName
        dJsonEntry["violations"] = oRules.extract_violation_dictionary()["violations"]

    return fExitStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bKeepProcessingFiles


def get_fixed_code(oVhdlFile, dConfig):
    sCode = "\n".join(oVhdlFile.get_lines()[1:])
    sLineSeparator = dConfig.get("linesep") if dConfig is not None else None
    if sLineSeparator:
        sCode = sCode.replace("\n", sLineSeparator)
    return sCode


def write_vhdl_file(oVhdlFile, dConfig):
    tmpfile = f"{oVhdlFile.filename}.tmp"
    myStat = os.stat(oVhdlFile.filename)
    sEncoding = oVhdlFile.sEncoding
    try:
        with open(tmpfile, "w", encoding=sEncoding, newline=dConfig.get("linesep")) as oFile:
            oFile.write("\n".join(oVhdlFile.get_lines()[1:]))
            oFile.write("\n")
        os.chmod(tmpfile, myStat.st_mode)
        os.replace(tmpfile, oVhdlFile.filename)
    except PermissionError as err:
        print(err, "Could not write fixes back to file.")
    finally:
        try:
            os.remove(tmpfile)
        except FileNotFoundError:
            pass


def create_junit_testcase(sVhdlFileName, oException):
    """
    Creates JUnit XML file listing all violations found.

    Parameters:

      sVhdlFileName (string)

    Returns: (junit testcase object)
    """
    oTestcase = junit.testcase(sVhdlFileName, str(0))
    oFailure = junit.failure("Failure")
    oFailure.add_text(oException.message)
    oTestcase.add_failure(oFailure)

    return oTestcase
