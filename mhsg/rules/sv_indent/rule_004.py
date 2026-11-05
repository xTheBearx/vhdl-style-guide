# -*- coding: utf-8 -*-

from mhsg import language, parser, violation
from mhsg.rules.sv_tree import before_errors, elements
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

lTokens = [tokens.token]
PATTERNS = ("SimpleAssignmentPattern", "StructuredAssignmentPattern", "ReplicatedAssignmentPattern")


class rule_004(Rule):
    """
    This rule checks the indent of an assignment pattern written over several lines, as Verible's formatter lays it
    out: when the opening '{ ends its line, each element that starts a line is indented **continuation_indent**
    levels, 1 by default, more than the line of the '{, and a closing } that starts a line is at the level of that
    line. A pattern in an element is indented from the line of its own '{. As Verible does, the elements of a pattern
    that is the value of a continuous assign are indented one level more, and its closing } one level.

    A pattern whose first element is on the line of its '{ is left as written.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           cfg = '{
             mode: 2'b01,
               size: 4'd8
             };
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           cfg = '{
               mode: 2'b01,
               size: 4'd8
           };
       end
    """

    def __init__(self):
        super().__init__(lTokens)
        self.languages = (language.SYSTEMVERILOG,)
        self.continuation_indent = 1
        self.configuration.append("continuation_indent")
        # After sv_indent_002, which leaves these lines indented more than their statement
        self.subphase = 3

    def _get_tokens_of_interest(self, oFile):
        if getattr(oFile, "dNodes", None) is None:
            return []
        lAll = oFile.lAllObjects
        dIndex = {id(o): i for i, o in enumerate(lAll)}
        # The first token of the line of each token, and the lines by their first token
        dLineFirst = {}
        oFirst = None
        bLineStart = True
        for oItem in lAll:
            if isinstance(oItem, parser.carriage_return):
                bLineStart = True
                continue
            if isinstance(oItem, parser.whitespace):
                continue
            if bLineStart:
                oFirst = oItem
                bLineStart = False
            dLineFirst[id(oItem)] = oFirst
        dLines = {}
        for oToi in oFile.get_tokens_at_beginning_of_line_matching(self.lTokens):
            dLines[id(oToi.get_tokens()[-1])] = oToi
        iLevel = int(self.continuation_indent) * self.indent_size
        dWanted = {}
        lPatterns = sorted(oFile.nodes(*PATTERNS), key=lambda o: o.openBrace.location.offset)
        for oPattern in lPatterns:
            oOpen = oFile.token_at(oPattern.openBrace)
            oClose = oFile.token_at(oPattern.closeBrace)
            if oOpen is None or oClose is None or id(oOpen) not in dIndex or not ends_line(lAll, dIndex[id(oOpen)]):
                continue
            oOpenLine = dLineFirst.get(id(oOpen))
            if oOpenLine is None or id(oOpenLine) not in dLines:
                continue
            # The level the line of the '{ has, or will have: that of sv_indent_001 for a line that starts an item, that of
            # an outer pattern for one of its elements, else the line as written
            iBase = dWanted.get(id(oOpenLine))
            if iBase is None and oOpenLine.get_indent() is not None:
                iBase = oOpenLine.get_indent() * self.indent_size
            if iBase is None:
                iBase = indent_of(dLines[id(oOpenLine)])
            if iBase is None:
                continue
            bAssign = continuous_assign(oPattern)
            iItems = iBase + iLevel * (2 if bAssign else 1)
            for oItem in elements(oPattern.items):
                oToken = oFile.token_at(oItem.getFirstToken())
                if oToken is not None and id(oToken) in dLines:
                    dWanted[id(oToken)] = iItems
            if id(oClose) in dLines:
                dWanted[id(oClose)] = iBase + (iLevel if bAssign else 0)
        lReturn = []
        for iId, iWanted in dWanted.items():
            oToi = dLines[iId]
            oToi.dMetaData["wanted"] = iWanted
            lReturn.append(oToi)
        lReturn.sort(key=lambda o: o.get_start_index())
        return before_errors(oFile, lReturn)

    def _analyze(self, lToi):
        for oToi in lToi:
            iActual = indent_of(oToi)
            iWanted = oToi.dMetaData["wanted"]
            if iActual is None or self.indent_style != "spaces" or iActual == iWanted:
                continue
            oViolation = violation.New(oToi.get_line_number(), oToi, f"Indent the line of the assignment pattern by {iWanted} spaces")
            oViolation.set_action(iWanted)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lLine = oViolation.get_tokens()
        iWanted = oViolation.get_action()
        lNew = ([parser.whitespace(" " * iWanted)] if iWanted > 0 else []) + [lLine[-1]]
        oViolation.set_tokens(lNew)


def indent_of(oToi):
    """The spaces before the first token of a line, or None when there is a tab."""
    lLine = oToi.get_tokens()
    sWhitespace = lLine[0].get_value() if len(lLine) == 2 else ""
    return None if "\t" in sWhitespace else len(sWhitespace)


def ends_line(lAll, iIndex):
    """Whether the token at an index is the last code on its line: only whitespace and comments follow it."""
    for oItem in lAll[iIndex + 1 :]:
        if isinstance(oItem, parser.carriage_return):
            return True
        if not isinstance(oItem, (parser.whitespace, parser.comment)):
            return False
    return True


def continuous_assign(oPattern):
    """Whether a pattern is the value of a continuous assign."""
    oExpression = oPattern.parent
    oAssignment = getattr(oExpression, "parent", None)
    oStatement = getattr(oAssignment, "parent", None)
    return oAssignment is not None and oAssignment.kind.name == "AssignmentExpression" and oStatement is not None and oStatement.kind.name == "ContinuousAssign"
