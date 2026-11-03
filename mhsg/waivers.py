# -*- coding: utf-8 -*-
"""
Waivers: findings accepted with a justification, from the waivers section of a configuration:

    waivers:
      - rule: lint_012
        file: rtl/sync/*.vhd
        line: 42
        message: "*sync_r*"
        justification: The synchronizer flip-flops have no reset by design
        reviewer: A. Reviewer

A finding a waiver matches is not reported as a violation and does not fail the run; it is listed as waived, with
its justification, in the reports. rule (a rule identifier, an alias, or a pattern such as sv_lint_*) and
justification are required; file, line and message narrow the waiver. Code tags disable a rule on a line too, but
leave no record; a waiver is listed in every report.

The crossings of clock domain analysis have waivers of their own, in the cdc section of the design.
"""

import fnmatch
import os

from mhsg import exceptions, rule_aliases

KEYS = ("rule", "file", "line", "message", "justification", "reviewer")


class Waiver:
    def __init__(self, iIndex, dWaiver):
        # The position of the waiver in the configuration, from 1, which reports use to name it
        self.index = iIndex
        self.rule = rule_aliases.get_rule_id(str(dWaiver["rule"]).strip())
        self.file = os.path.expandvars(str(dWaiver["file"])) if dWaiver.get("file") is not None else None
        oLine = dWaiver.get("line")
        self.lines = None if oLine is None else [int(o) for o in (oLine if isinstance(oLine, list) else [oLine])]
        self.message = str(dWaiver["message"]) if dWaiver.get("message") is not None else None
        self.justification = str(dWaiver["justification"]).strip()
        self.reviewer = str(dWaiver["reviewer"]).strip() if dWaiver.get("reviewer") is not None else None

    def describe(self):
        """A short name of the waiver for messages: its position, rule and file."""
        return f"waiver {self.index} (rule {self.rule}" + (f", file {self.file}" if self.file else "") + ")"

    def applies_to_file(self, sFile):
        """Whether the waiver can match findings of a file: a pattern without a directory matches the file name."""
        if self.file is None:
            return True
        if sFile is None:
            return False
        if os.sep not in self.file and "/" not in self.file:
            return fnmatch.fnmatchcase(os.path.basename(sFile), self.file)
        return fnmatch.fnmatchcase(os.path.normpath(os.path.abspath(sFile)), os.path.normpath(os.path.abspath(self.file)))

    def applies_to_rule(self, sRule):
        return sRule == self.rule or fnmatch.fnmatchcase(sRule, self.rule)

    def matches(self, sRule, sFile, iLine, sMessage):
        if not self.applies_to_rule(sRule) or not self.applies_to_file(sFile):
            return False
        if self.lines is not None and iLine not in self.lines:
            return False
        if self.message is not None and not fnmatch.fnmatchcase(sMessage or "", self.message):
            return False
        return True

    def entry(self):
        """The waiver as reports list it."""
        dReturn = {"waiver": self.index, "justification": self.justification}
        if self.reviewer:
            dReturn["reviewer"] = self.reviewer
        return dReturn


def from_configuration(dConfig):
    """Returns the waivers of a configuration, or raises a ConfigurationError for one that is not valid."""
    lWaivers = (dConfig or {}).get("waivers")
    if lWaivers is None:
        return []
    if not isinstance(lWaivers, list):
        raise exceptions.ConfigurationError("ERROR: waivers is a list of waivers, each with a rule and a justification")
    lReturn = []
    for iIndex, dWaiver in enumerate(lWaivers, start=1):
        if not isinstance(dWaiver, dict) or not dWaiver.get("rule"):
            raise exceptions.ConfigurationError(f"ERROR: waiver {iIndex} needs a rule")
        lUnknown = sorted(str(s) for s in dWaiver if s not in KEYS)
        if lUnknown:
            raise exceptions.ConfigurationError(f"ERROR: waiver {iIndex} has unknown keys {', '.join(lUnknown)}; the keys are {', '.join(KEYS)}")
        if not str(dWaiver.get("justification") or "").strip():
            raise exceptions.ConfigurationError(f"ERROR: waiver {iIndex} (rule {dWaiver['rule']}) needs a justification")
        try:
            lReturn.append(Waiver(iIndex, dWaiver))
        except (TypeError, ValueError):
            raise exceptions.ConfigurationError(f"ERROR: waiver {iIndex} (rule {dWaiver['rule']}) has a line that is not a number") from None
    return lReturn


def first_match(lWaivers, sRule, sFile, iLine, sMessage):
    """Returns the first waiver that matches a finding, or None."""
    for oWaiver in lWaivers:
        if oWaiver.matches(sRule, sFile, iLine, sMessage):
            return oWaiver
    return None


def apply(oRule, sFile, lWaivers, dUse):
    """
    Moves the violations of a rule that a waiver matches to the rule's waived list, as (violation, waiver). dUse records
    for each waiver that could match in this file, by index, whether it matched: True, or False if it did not.
    """
    if not lWaivers:
        return
    sRule = oRule.get_unique_id()
    for oWaiver in lWaivers:
        if oWaiver.applies_to_rule(sRule) and oWaiver.applies_to_file(sFile):
            dUse.setdefault(oWaiver.index, False)
    if not oRule.violations:
        return
    lKept = []
    for oViolation in oRule.violations:
        oWaiver = first_match(lWaivers, sRule, sFile, oViolation.get_line_number(), oViolation.get_solution())
        if oWaiver is None:
            lKept.append(oViolation)
        else:
            oRule.waived.append((oViolation, oWaiver))
            dUse[oWaiver.index] = True
    oRule.violations = lKept


def unused(lWaivers, lUses):
    """
    Returns the waivers that could match findings in the files of a run, as their rule ran on a file they name, but
    matched none: they may be out of date.
    """
    setUsed = {iIndex for dUse in lUses for iIndex, bUsed in dUse.items() if bUsed}
    setApplicable = {iIndex for dUse in lUses for iIndex in dUse}
    return [o for o in lWaivers if o.index in setApplicable and o.index not in setUsed]
