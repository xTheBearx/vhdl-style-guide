# -*- coding: utf-8 -*-
"""
Base class of the SystemVerilog rules that align a column of tokens over consecutive lines, as Verible's formatter
does: the names of port declarations, the parentheses of named connections, the = of assignments and parameters, and
the statements of case items.

A rule gives groups of rows: the tokens to align, one on each line, such as the names of the ports of a list. By default the rule infers
what the author meant, as Verible does: when aligning moves no token by more than 2 spaces, align; when no row has more
than 2 spaces beyond the least, keep them flush left; when a row has 4 or more, align; otherwise leave the group as it
is. **policy** set to align or flush_left forces one or the other.
"""

import importlib

from mhsg import parser
from mhsg.rule_group import alignment
from mhsg.rules.sv_tree import Problem, TreeRule
from mhsg.vhdlFile import utils

# mhsg.svFile exports the class svFile under the name of its module
svFile = importlib.import_module("mhsg.svFile.svFile")

POLICIES = ("infer", "align", "flush_left")


class Rule(TreeRule, alignment.Rule):
    def __init__(self):
        super().__init__()
        self.fixable = True
        self.policy = "infer"
        self.blank_line_ends_group = "no"
        self.configuration.extend(["policy", "blank_line_ends_group"])
        # After the case items, whose alignment moves what follows their colons, and after the columns before the
        # names of declarations, which move the names (sv_alignment_009 and 010)
        self.subphase = 4
        # The fewest spaces between the token before the column and the token in it
        self.minimum_spaces = 1

    def alignment_groups(self, oFile):
        """
        Yields lists of rows of a group: (item, syntax token to align), where the item is the syntax node of the row,
        such as a declaration; None for an item that ends a run; or False for an item that has nothing in the column
        but does not end the run, such as a port without a packed dimension. A row counts only when its item starts
        its line.
        """
        raise NotImplementedError

    def problems(self, oFile):
        dPlaces, dBefore, setLineStarts, setAfterTab = oFile.cached("sv_align.places", lambda: places(oFile.lAllObjects))
        setBlankLines = oFile.cached("sv_align.blank_lines", lambda: blank_lines(oFile.lAllObjects))
        bBlankEnds = utils.convert_yes_no_option_to_boolean(self.blank_line_ends_group)
        for lGroup in self.alignment_groups(oFile):
            lRows = []
            for tRow in lGroup:
                if tRow is False:
                    continue
                oItem, oSyntaxTarget = tRow if tRow is not None else (None, None)
                oTarget = oFile.token_at(oSyntaxTarget) if oSyntaxTarget is not None else None
                oLeft = dBefore.get(id(oTarget)) if oTarget is not None else None
                oStart = oFile.token_at(oItem.getFirstToken()) if oItem is not None else None
                # A tab before the token makes its column unknown; the tab rules replace tabs first
                if oLeft is None or id(oTarget) not in dPlaces or oStart is None or id(oStart) not in setLineStarts or id(oTarget) in setAfterTab:
                    lRows.append(None)
                    continue
                (iLeftLine, iLeftColumn), (iLine, iColumn) = dPlaces[id(oLeft)], dPlaces[id(oTarget)]
                if iLeftLine != iLine:
                    lRows.append(None)
                    continue
                iEnd = iLeftColumn + len(oLeft.get_value())
                lRows.append((oLeft, oTarget, iLine, iEnd, iColumn - iEnd))
            for lRun in runs(lRows, setBlankLines if bBlankEnds else set()):
                yield from self.align(lRun)

    def align(self, lRows):
        if len(lRows) < 2:
            return
        iMinimum = self.minimum_spaces
        iColumn = max(iEnd + iMinimum for _, _, _, iEnd, _ in lRows)
        sPolicy = self.policy if self.policy in POLICIES else "infer"
        if sPolicy == "infer":
            iMove = max(iColumn - iEnd - iMinimum for _, _, _, iEnd, _ in lRows)
            iExcess = max(iSpaces - iMinimum for _, _, _, _, iSpaces in lRows)
            if iMove <= 2:
                sPolicy = "align"
            elif iExcess <= 2:
                sPolicy = "flush_left"
            elif iExcess >= 4:
                sPolicy = "align"
            else:
                return
        for oLeft, oTarget, _, iEnd, iSpaces in lRows:
            iWanted = iColumn - iEnd if sPolicy == "align" else iMinimum
            if iSpaces != iWanted:
                sWhat = (
                    f"Align {oTarget.get_value()} in column {iColumn + 1}" if sPolicy == "align" else f"Use {iMinimum} space(s) before {oTarget.get_value()}"
                )
                yield Problem(oLeft, sWhat, oTarget, {"spaces": iWanted})

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        iSpaces = oViolation.get_action()["spaces"]
        lNew = [lTokens[0]]
        if iSpaces > 0:
            lNew.append(parser.whitespace(" " * iSpaces))
        lNew.append(lTokens[-1])
        oViolation.set_tokens(lNew)

    def fix(self, oFile, dFixOnly=None):
        # Only spaces change, so the file is not parsed again; a comment continuing a trailing comment moves with it
        super(TreeRule, self).fix(oFile, dFixOnly)
        if self.fixable and svFile.realign_comment_continuations(oFile.lAllObjects):
            oFile.update_token_map()


def places(lTokens):
    """
    Returns ({id of token: (line, column)}, {id of token: the token before it on its line}, ids of the tokens that start
    a line, ids of the tokens after a tab on their line) for the tokens of a file, columns from 0; whitespace and
    comments are not tokens before another.
    """
    dReturn = {}
    dBefore = {}
    setLineStarts = set()
    setAfterTab = set()
    bTab = False
    iLine, iColumn = 1, 0
    oPrevious = None
    bLineStart = True
    for oToken in lTokens:
        if isinstance(oToken, parser.carriage_return):
            iLine += 1
            iColumn = 0
            oPrevious = None
            bLineStart = True
            bTab = False
            continue
        dReturn[id(oToken)] = (iLine, iColumn)
        if bTab:
            setAfterTab.add(id(oToken))
        bTab = bTab or "\t" in oToken.get_value()
        iColumn += len(oToken.get_value())
        if isinstance(oToken, (parser.whitespace, parser.blank_line)):
            continue
        if oPrevious is not None:
            dBefore[id(oToken)] = oPrevious
        elif bLineStart and not isinstance(oToken, parser.comment):
            setLineStarts.add(id(oToken))
        bLineStart = False
        oPrevious = None if isinstance(oToken, parser.comment) else oToken
    return dReturn, dBefore, setLineStarts, setAfterTab


def blank_lines(lTokens):
    setReturn = set()
    iLine = 1
    for oToken in lTokens:
        if isinstance(oToken, parser.carriage_return):
            iLine += 1
        elif isinstance(oToken, parser.blank_line):
            setReturn.add(iLine)
    return setReturn


def runs(lRows, setBlankLines):
    """Splits rows into runs of rows that can be aligned: a missing row, or a blank line between two, ends a run."""
    lRun = []
    for tRow in lRows:
        if tRow is None:
            yield lRun
            lRun = []
            continue
        if lRun and any(i in setBlankLines for i in range(lRun[-1][2] + 1, tRow[2])):
            yield lRun
            lRun = []
        if lRun and tRow[2] == lRun[-1][2]:
            # Two rows on one line cannot be aligned with each other
            yield lRun
            lRun = []
        lRun.append(tRow)
    yield lRun
