# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule

reNumber = re.compile(r"^(\d[\d_]*(\.\d[\d_]*)?([eE][+-]?\d+)?|\d+#[0-9a-fA-F_.]+#([eE][+-]?\d+)?)$")
TIME_UNITS = ("fs", "ps", "ns", "us", "ms", "sec", "min", "hr")


class rule_034(Rule):
    """
    This rule checks for numbers written in statements, other than 0 and 1.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (CP3).

    A number in a statement, such as a count limit or a width, says nothing of what it stands for and must be found and
    changed everywhere it is used. Declare a constant or a generic with a name instead. Numbers in declarations, such
    as the values of constants and the ranges of types, and fixed bit positions, such as data(3) or data(7 downto 4),
    are not checked. The allowed option lists the numbers allowed in statements.

    **Violation**

    .. code-block:: vhdl

       if count = 99 then

    **Fix**

    .. code-block:: vhdl

       constant c_last_count : natural := 99;
       ...
       if count = c_last_count then
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a named constant or generic"
        self.allowed_numbers = ["0", "1"]
        self.configuration.append("allowed_numbers")

    def check(self, oModel, oFile):
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        setAllowed = {str(s) for s in self.allowed_numbers}
        lReported = []
        for lTokens in statement_tokens(oModel, oFile):
            setConstantGroups = constant_groups(lTokens)
            for iPosition, oToken in enumerate(lTokens):
                sValue = oToken.get_value() or ""
                if not reNumber.match(sValue) or sValue in setAllowed or id(oToken) in lReported:
                    continue
                if next_value(lTokens, iPosition) in TIME_UNITS or iPosition in setConstantGroups:
                    continue
                lReported.append(id(oToken))
                self.report(oFile, dIndexes[id(oToken)], f"Replace {sValue} by a named constant or generic")


def statement_tokens(oModel, oFile):
    """Yields the tokens of each statement of the processes and of each concurrent assignment, and conditions."""
    lTokens = oFile.lAllObjects
    for oArchitecture in oModel.architectures:
        for oAssignment in oArchitecture.assignments:
            yield until_semicolon(lTokens, oAssignment.index)
        for oProcess in oArchitecture.processes:
            for oStatement in model.walk(oProcess.statements):
                if isinstance(oStatement, (model.Assignment, model.Other)):
                    yield until_semicolon(lTokens, oStatement.index)
                elif isinstance(oStatement, model.If):
                    for tBranch in oStatement.branches:
                        yield list(tBranch[0] or [])
                elif isinstance(oStatement, model.Loop):
                    yield list(oStatement.header)


def until_semicolon(lTokens, iIndex):
    lReturn = []
    for oToken in lTokens[iIndex:]:
        if isinstance(oToken, model.parser.semicolon):
            break
        lReturn.append(oToken)
    return lReturn


def next_value(lTokens, iPosition):
    for oToken in lTokens[iPosition + 1 :]:
        if not model.is_trivia(oToken):
            return (oToken.get_value() or "").lower()
    return ""


def constant_groups(lTokens):
    """
    Returns the positions of the tokens in parentheses that hold only numbers and directions, such as the index of
    data(3) or the slice of data(7 downto 4): fixed bit positions, which are not reported.
    """
    setReturn = set()
    lStack = []
    for iPosition, oToken in enumerate(lTokens):
        if isinstance(oToken, model.parser.open_parenthesis):
            lStack.append([])
        elif isinstance(oToken, model.parser.close_parenthesis) and lStack:
            lGroup = lStack.pop()
            lValues = [lTokens[i] for i in lGroup if not model.is_trivia(lTokens[i])]
            if lValues and all(reNumber.match(o.get_value() or "") or model.kind(o)[0] == "direction" for o in lValues):
                setReturn.update(lGroup)
            if lStack:
                lStack[-1].extend(lGroup)
        elif lStack:
            lStack[-1].append(iPosition)
    return setReturn
