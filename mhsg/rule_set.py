# -*- coding: utf-8 -*-
"""
Rule sets map the checks of a coding standard, such as the DO-254 coding standards, to the rules that implement them.

A rule set is a YAML file. Built in sets are in mhsg/rule_sets and are selected by name; a user's own set is selected by its path.
When a rule set is applied, each rule it lists is enabled, is reported with the severity of its check, and is labelled
with the check identifier in reports, for example "DO254-CP2 (lint_001)". The severity only changes reporting: whether
--fix fixes a rule still follows the rule's own severity.
"""

import os

import yaml

from mhsg import exceptions, severity

RULE_SET_DIRECTORY = os.path.join(os.path.dirname(__file__), "rule_sets")

# Severity names in decreasing order, used when a rule implements checks of different severities
SEVERITY_ORDER = ["Error", "Warning", "Note"]


class Check:
    def __init__(self, sId, dCheck):
        self.id = sId
        self.title = dCheck.get("title", "")
        self.severity = dCheck.get("severity")
        self.rules = list(dCheck.get("rules") or [])
        # Rule groups, such as indent, whose rules all implement the check
        self.groups = list(dCheck.get("groups") or [])
        # False to label the rules without enabling them, for checks that need project settings first
        self.enable = dCheck.get("enable", True)
        self.configuration = dict(dCheck.get("configuration") or {})
        # implemented, planned, design or manual
        self.status = dCheck.get("status", "implemented" if self.rules or self.groups else "planned")
        self.note = dCheck.get("note", "")


class RuleSet:
    def __init__(self, dRuleSet, sFileName):
        self.filename = sFileName
        self.name = dRuleSet.get("name", os.path.splitext(os.path.basename(sFileName))[0])
        self.prefix = dRuleSet.get("prefix", self.name)
        self.version = str(dRuleSet.get("version", ""))
        self.title = dRuleSet.get("title", "")
        self.source = dRuleSet.get("source", "")
        self.checks = [Check(str(sId), dCheck or {}) for sId, dCheck in (dRuleSet.get("checks") or {}).items()]
        # Rule sets this one includes; their checks keep their own labels
        self.parents = []

    def all_sets(self):
        """Returns the included rule sets, depth first, and then this one; each set once."""
        lReturn = []
        for oParent in self.parents:
            for oRuleSet in oParent.all_sets():
                if oRuleSet.filename not in [o.filename for o in lReturn]:
                    lReturn.append(oRuleSet)
        lReturn.append(self)
        return lReturn

    def label(self, oCheck):
        return self.prefix + "-" + oCheck.id

    def apply(self, oRuleList, oSeverityList, bLintOnly=False):
        """
        Enables and labels the rules of the set, sets their severities and options, and with bLintOnly disables every other rule.
        Raises a ConfigurationError for a rule or severity that does not exist.
        """
        severity.add_note(oSeverityList)
        dRules = {oRule.get_unique_id(): oRule for oRule in oRuleList.rules}
        dSeverities = {}
        setListed = set()
        lChecks = [(oRuleSet, oCheck) for oRuleSet in self.all_sets() for oCheck in oRuleSet.checks]
        for oRuleSet, oCheck in lChecks:
            for sRule, dAttributes in oCheck.configuration.items():
                oRule = get_rule(dRules, sRule, oRuleSet)
                for sAttribute, oValue in (dAttributes or {}).items():
                    set_attribute(oRule, sAttribute, oValue, oSeverityList, oRuleSet)
                setListed.add(oRule.get_unique_id())
            for sRule in oCheck.rules + rules_in_groups(oRuleList, oCheck.groups):
                oRule = get_rule(dRules, sRule, oRuleSet)
                if oCheck.enable:
                    oRule.disable = False
                oRule.rule_set_labels.append(oRuleSet.label(oCheck))
                setListed.add(oRule.get_unique_id())
                if oCheck.severity is not None:
                    dSeverities.setdefault(oRule.get_unique_id(), []).append(oCheck.severity)
        for sRule, lSeverities in dSeverities.items():
            set_attribute(dRules[sRule], "severity", most_severe(lSeverities), oSeverityList, self)
        if bLintOnly:
            for oRule in oRuleList.rules:
                if oRule.get_unique_id() not in setListed:
                    oRule.disable = True


def enable_lint_rules(oRuleList, bLintOnly=False):
    """Lint mode without a rule set: enables every lint rule, and with bLintOnly disables every other rule."""
    for oRule in oRuleList.rules:
        if oRule.lint:
            oRule.disable = False
        elif bLintOnly:
            oRule.disable = True


def apply(oRuleList, oConfig):
    """Applies lint mode, if it is on, to a rule list: the rule set if there is one, otherwise all lint rules."""
    sMode = getattr(oConfig, "lint_mode", None)
    if sMode is None:
        return
    bLintOnly = sMode == "lint_only"
    if oConfig.rule_set is None:
        enable_lint_rules(oRuleList, bLintOnly)
    else:
        oConfig.rule_set.apply(oRuleList, oConfig.severity_list, bLintOnly)


def configure_lint_mode(oConfig, commandLineArguments):
    """
    Sets the lint mode and rule set from the command line, or from the lint, lint_only and rule_set keys of the configuration.
    The command line takes precedence. Lint mode uses the do254 rule set unless another one, or none, is given.
    """
    dConfig = oConfig.dConfig or {}
    if getattr(commandLineArguments, "lint_only", False) or dConfig.get("lint_only", False):
        oConfig.lint_mode = "lint_only"
    elif getattr(commandLineArguments, "lint", False) or dConfig.get("lint", False):
        oConfig.lint_mode = "lint"
    if oConfig.lint_mode is None:
        return
    if oConfig.severity_list is not None:
        severity.add_note(oConfig.severity_list)
    sRuleSet = getattr(commandLineArguments, "rule_set", None) or dConfig.get("rule_set") or "do254"
    oConfig.rule_set = load(sRuleSet)


def rules_in_groups(oRuleList, lGroups):
    """Returns the identifiers of the rules in any of the groups, leaving out deprecated rules."""
    if not lGroups:
        return []
    return [o.get_unique_id() for o in oRuleList.rules if not o.deprecated and any(sGroup in o.groups for sGroup in lGroups)]


def get_rule(dRules, sRule, oRuleSet):
    if sRule not in dRules:
        raise exceptions.ConfigurationError(f"ERROR: rule {sRule} in rule set {oRuleSet.name} ({oRuleSet.filename}) does not exist")
    return dRules[sRule]


def set_attribute(oRule, sAttribute, oValue, oSeverityList, oRuleSet):
    if sAttribute == "severity":
        oSeverity = oSeverityList.get_severity_named(oValue)
        if oSeverity is None:
            raise exceptions.ConfigurationError(f"ERROR: severity {oValue} in rule set {oRuleSet.name} does not exist")
        # Only the reported severity changes: whether --fix fixes the rule still follows its own severity
        oRule.report_severity = oSeverity
    elif sAttribute in oRule.configuration:
        setattr(oRule, sAttribute, oValue)
    else:
        raise exceptions.ConfigurationError(f"ERROR: rule {oRule.get_unique_id()} in rule set {oRuleSet.name} has no option {sAttribute}")


def most_severe(lSeverities):
    lKnown = [s for s in lSeverities if s in SEVERITY_ORDER]
    if lKnown:
        return min(lKnown, key=SEVERITY_ORDER.index)
    return lSeverities[0]


def get_built_in_rule_sets():
    return sorted(os.path.splitext(s)[0] for s in os.listdir(RULE_SET_DIRECTORY) if s.endswith(".yaml"))


def load(sNameOrPath, sDirectory=None, lLoading=None):
    """
    Returns the rule set with a built in name, such as do254, or in a YAML file. Returns None for "none".
    A rule set can include others with the extends key, by name or by a path relative to its own file.
    Raises a ConfigurationError if it cannot be found or read.
    """
    if sNameOrPath is None or sNameOrPath.lower() == "none":
        return None
    sFileName = os.path.join(RULE_SET_DIRECTORY, sNameOrPath.lower() + ".yaml")
    if not os.path.isfile(sFileName):
        sFileName = os.path.expandvars(sNameOrPath)
        if sDirectory is not None and not os.path.isabs(sFileName):
            sFileName = os.path.join(sDirectory, sFileName)
    if not os.path.isfile(sFileName):
        sBuiltIn = ", ".join(get_built_in_rule_sets())
        raise exceptions.ConfigurationError(f"ERROR: rule set {sNameOrPath} is not a built in rule set ({sBuiltIn}) or a file")
    if os.path.abspath(sFileName) in (lLoading or []):
        raise exceptions.ConfigurationError(f"ERROR: rule set {sFileName} includes itself through extends")
    try:
        with open(sFileName, encoding="utf-8") as oFile:
            dRuleSet = yaml.safe_load(oFile)
    except (OSError, yaml.YAMLError) as e:
        raise exceptions.ConfigurationError(f"ERROR: could not read rule set {sFileName}: {e}") from e
    if not isinstance(dRuleSet, dict):
        raise exceptions.ConfigurationError(f"ERROR: rule set {sFileName} is not a mapping")
    lLoading = (lLoading or []) + [os.path.abspath(sFileName)]
    oRuleSet = RuleSet(dRuleSet, sFileName)
    lExtends = dRuleSet.get("extends") or []
    for sParent in [lExtends] if isinstance(lExtends, str) else lExtends:
        oParent = load(sParent, os.path.dirname(sFileName), lLoading)
        if oParent is not None:
            oRuleSet.parents.append(oParent)
    return oRuleSet


STATUS_TEXT = {
    "implemented": "Implemented",
    "planned": "Planned, per-file lint",
    "design": "Planned, design analysis",
    "manual": "Manual review",
}


def coverage_table(oRuleSet):
    """Returns a reStructuredText table of the checks of a rule set: severity, status and the rules that implement them."""
    lRows = [("Check", "Title", "Severity", "Status", "Rules")]
    for oCheck in oRuleSet.checks:
        lRules = [f":code:`{s}`" for s in oCheck.rules] + [f"group :code:`{s}`" for s in oCheck.groups]
        sStatus = STATUS_TEXT.get(oCheck.status, oCheck.status)
        if oCheck.status == "implemented" and not oCheck.enable:
            sStatus = "Implemented, enable after configuring"
        elif oCheck.status == "implemented" and oCheck.rules and all(s.startswith("design_") for s in oCheck.rules):
            sStatus = "Implemented, design analysis"
        lRows.append((oRuleSet.prefix + "-" + oCheck.id, oCheck.title, oCheck.severity or "", sStatus, ", ".join(lRules)))
    lWidths = [max(len(tRow[i]) for tRow in lRows) for i in range(5)]
    sRule = "+" + "+".join("-" * (i + 2) for i in lWidths) + "+"
    lLines = [sRule]
    for iRow, tRow in enumerate(lRows):
        lLines.append("| " + " | ".join(s.ljust(lWidths[i]) for i, s in enumerate(tRow)) + " |")
        lLines.append(sRule.replace("-", "=") if iRow == 0 else sRule)
    return "\n".join(lLines) + "\n"
