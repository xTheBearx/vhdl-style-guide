# -*- coding: utf-8 -*-

from mhsg import parser, token, violation
from mhsg.rule_group import blank_line
from mhsg.rules import utils as rules_utils
from mhsg.rules.remove_excessive_blank_lines_below_line_ending_with_token import (
    check_if_override_exists,
)
from mhsg.vhdlFile import utils


class blank_line_below_line_ending_with_token(blank_line.Rule):
    """
    Checks for a blank line below a line ending with a given token

    Parameters
    ----------

    name : string
       The group the rule belongs to.

    identifier : string
       unique identifier.  Usually in the form of 00N.

    token: token object type list
       token object that a blank line below should appear
    """

    def __init__(self, lTokens, lAllowTokens=None):
        super().__init__()
        self.lTokens = lTokens
        self.lHierarchyLimits = None
        if lAllowTokens is None:
            self.lAllowTokens = []
        else:
            self.lAllowTokens = lAllowTokens
        self.style = "require_blank_line"
        self.configuration.append("style")
        # With the no_blank_line style, one blank line is allowed above a line containing one of these tokens
        self.lOverrides = []

    def _get_tokens_of_interest(self, oFile):
        if self.style.startswith("require_blank_line"):
            if self.lHierarchyLimits is None:
                return oFile.get_line_below_line_ending_with_token(self.lTokens)
            else:
                return oFile.get_line_below_line_ending_with_token_with_hierarchy(self.lTokens, self.lHierarchyLimits)
        elif self.style == "no_blank_line":
            lToi = oFile.get_blank_lines_below_line_ending_with_token(self.lTokens, self.lHierarchyLimits)
            _mark_overrides(oFile, lToi, self.lOverrides)
            return lToi

    def _analyze(self, lToi):
        if self.style == "require_blank_line":
            _analyze_require_blank_line(self, lToi, self.lAllowTokens)
        elif self.style == "no_blank_line":
            _analyze_no_blank_line(self, lToi, self.lAllowTokens)
        elif self.style == "require_blank_line_unless_pragma":
            self.lAllowTokens.append(token.pragma.pragma)
            _analyze_require_blank_line(self, lToi, self.lAllowTokens)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        dAction = oViolation.get_action()
        if dAction["action"] == "Insert":
            rules_utils.insert_carriage_return(lTokens, 0)
            rules_utils.insert_blank_line(lTokens, 0)
            oViolation.set_tokens(lTokens)
        elif dAction["action"] == "Remove":
            oViolation.set_tokens(lTokens[0 : dAction.get("keep", 0)])


def _analyze_require_blank_line(self, lToi, lAllowTokens):
    for oToi in lToi:
        lTokens = oToi.get_tokens()
        if _is_allowed_token(lAllowTokens, lTokens):
            continue
        if len(lTokens) == 1:
            if isinstance(lTokens[0], parser.blank_line):
                continue
        sSolution = "Insert blank line below"
        oViolation = violation.New(oToi.get_line_number() - 1, oToi, sSolution)
        dAction = {}
        dAction["action"] = "Insert"
        oViolation.set_action(dAction)
        self.add_violation(oViolation)


def _mark_overrides(oFile, lToi, lOverrides):
    if len(lOverrides) == 0:
        return
    for oToi in lToi:
        iLine = oToi.get_line_number()
        for oToken in oToi.get_tokens():
            iLine = utils.increment_line_number(iLine, oToken)
        oToi.set_meta_data("allow_one_blank_line", check_if_override_exists(oFile, iLine, lOverrides))


def _analyze_no_blank_line(self, lToi, lAllowTokens):
    for oToi in lToi:
        sSolution = "Remove blank lines below"
        dAction = {}
        dAction["action"] = "Remove"
        if oToi.dMetaData.get("allow_one_blank_line", False):
            if len([oToken for oToken in oToi.get_tokens() if isinstance(oToken, parser.blank_line)]) <= 1:
                continue
            # Keep the first blank line and its carriage return
            dAction["keep"] = 2
        oViolation = violation.New(oToi.get_line_number() + 1, oToi, sSolution)
        oViolation.set_action(dAction)
        self.add_violation(oViolation)


def _is_allowed_token(lAllowTokens, lTokens):
    bSkip = False
    for oAllowToken in lAllowTokens:
        for oToken in lTokens:
            if isinstance(oToken, oAllowToken):
                bSkip = True
                break
        if bSkip:
            break
    return bSkip
