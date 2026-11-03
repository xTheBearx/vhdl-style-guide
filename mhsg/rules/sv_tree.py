# -*- coding: utf-8 -*-
"""
Base class of the SystemVerilog rules that look at constructs in the syntax tree, such as always blocks or labels.

A rule yields problems: the token to report and, for a rule that can fix it, the range of tokens its fix replaces.
After fixing, the file is parsed again, as a fix can change the structure the next rules look at.
"""

from pyslang.parsing import Token  # pylint: disable=import-error
from pyslang.syntax import SyntaxNode  # pylint: disable=import-error

from mhsg import language, violation
from mhsg.vhdlFile.extract import tokens as extract_tokens


class Problem:
    """
    A problem a rule found: oFirst, and oLast for a range, are the mhsg tokens the fix replaces, and the first is
    reported; dAction is whatever the rule's fix needs.
    """

    def __init__(self, oFirst, sSolution, oLast=None, dAction=None):
        self.first = oFirst
        self.last = oLast if oLast is not None else oFirst
        self.solution = sSolution
        self.action = dAction or {}


class TreeRule:  # pylint: disable=no-member
    """
    Mixin for a rule group class, such as structure.Rule, which it comes before in the bases of a rule; the rule
    gives it a problems(oFile) method. The members pylint cannot find come from that rule group class.
    """

    def __init__(self):
        super().__init__()
        self.languages = (language.SYSTEMVERILOG,)
        self.configuration_documentation_link = None
        self.fixable = False

    def problems(self, oFile):
        """Yields the Problems in a file."""
        raise NotImplementedError

    def _get_tokens_of_interest(self, oFile):
        if getattr(oFile, "dNodes", None) is None:
            return []
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        lReturn = []
        for oProblem in self.problems(oFile):
            iFirst = dIndexes.get(id(oProblem.first))
            iLast = dIndexes.get(id(oProblem.last))
            if iFirst is None or iLast is None:
                continue
            oToi = extract_tokens.New(iFirst, oFile.oTokenMap.get_line_number_of_index(iFirst), oFile.lAllObjects[iFirst : iLast + 1])
            oToi.dMetaData["problem"] = oProblem
            lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            oProblem = oToi.dMetaData["problem"]
            oViolation = violation.New(oToi.get_line_number(), oToi, oProblem.solution)
            oViolation.set_action(oProblem.action)
            self.add_violation(oViolation)

    def fix(self, oFile, dFixOnly=None):
        super().fix(oFile, dFixOnly)
        if self.fixable and self.had_violations and hasattr(oFile, "reparse"):
            oFile.reparse()


def descendants(oNode):
    """The syntax nodes under a node, depth first."""
    lStack = [oNode]
    while lStack:
        oItem = lStack.pop()
        for oChild in oItem:
            if isinstance(oChild, SyntaxNode):
                yield oChild
                lStack.append(oChild)


def child_tokens(oNode):
    """The tokens directly under a node, not in its child nodes."""
    return [o for o in oNode if isinstance(o, Token)]


def name_of(oToken):
    """The text of a syntax token, or "" for none."""
    return oToken.rawText if oToken is not None else ""


def first_token(oFile, oNode):
    """The mhsg token of the first token of a syntax node."""
    return oFile.token_at(oNode.getFirstToken())


def last_token(oFile, oNode):
    return oFile.token_at(oNode.getLastToken())
