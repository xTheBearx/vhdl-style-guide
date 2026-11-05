# -*- coding: utf-8 -*-

from mhsg import language, parser, violation
from mhsg.rules.sv_tree import before_errors, elements
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

lTokens = [tokens.token]
PATTERNS = ("SimpleAssignmentPattern", "StructuredAssignmentPattern", "ReplicatedAssignmentPattern")
# The lists this rule lays out: (node kind, opening field, items field, closing field)
LISTS = [(s, "openBrace", "items", "closeBrace") for s in PATTERNS] + [
    ("ArgumentList", "openParen", "parameters", "closeParen"),
    ("ConstraintBlock", "openBrace", "items", "closeBrace"),
]
# The nodes that end the search for the condition of an if: statements and declarations
STATEMENT_ENDS = ("Statement", "Declaration", "ContinuousAssign", "Item")


class rule_004(Rule):
    """
    This rule checks the indent of a list written over several lines, as Verible's formatter lays it out: the elements
    of an assignment pattern, the arguments of a call, and the constraints of a randomize with. When the opening '{,
    ( or { ends its line, each element that starts a line is indented **continuation_indent** levels, 1 by default,
    more than the line of the opening bracket, and a closing bracket that starts a line is at the level of that line.
    A list in an element is indented from the line of its own opening bracket. As Verible does, a list in the
    condition of an if is indented one level more, its closing bracket one level, and so are the elements of an
    assignment pattern that is the value of a continuous assign.

    A list whose first element is on the line of its opening bracket, such as arguments aligned after the
    parenthesis, is left as written; sv_indent_002 checks it.

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
        dLines = {}
        for oToi in oFile.get_tokens_at_beginning_of_line_matching(self.lTokens):
            dLines[id(oToi.get_tokens()[-1])] = oToi
        dWanted = expanded_lines(oFile, dLines, int(self.continuation_indent) * self.indent_size, self.indent_size)
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
            oViolation = violation.New(oToi.get_line_number(), oToi, f"Indent the line of the list by {iWanted} spaces")
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


def in_if_condition(oNode):
    """Whether a list is in the condition of an if, before the statement it is in ends the search."""
    oCurrent = oNode.parent
    while oCurrent is not None:
        sKind = oCurrent.kind.name
        if sKind == "ConditionalPredicate":
            return True
        if sKind.endswith(STATEMENT_ENDS):
            return False
        oCurrent = getattr(oCurrent, "parent", None)
    return False


def expanded_lists(oFile):
    """The lists whose opening bracket ends its line, outer before inner, with (opening, items, closing) fields."""
    dFields = {sKind: (sOpen, sItems, sClose) for sKind, sOpen, sItems, sClose in LISTS}
    lLists = [o for o in oFile.nodes(*dFields) if o.kind.name != "ConstraintBlock" or o.parent.kind.name == "ArrayOrRandomizeMethodExpression"]
    lLists.sort(key=lambda o: getattr(o, dFields[o.kind.name][0]).location.offset)
    return [(o, dFields[o.kind.name]) for o in lLists]


def expanded_lines(oFile, dLines, iLevel, iIndentSize):
    """
    {id of the first token of a line: the spaces it is indented by} for the lines this rule lays out, given dLines,
    {id of the first token of a line: its tokens of interest}; also used by sv_indent_002, which leaves them alone.
    """
    lAll = oFile.lAllObjects
    dIndex = {id(o): i for i, o in enumerate(lAll)}
    # The first token of the line of each token
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
    dWanted = {}
    for oList, (sOpen, sItems, sClose) in expanded_lists(oFile):
        oOpen = oFile.token_at(getattr(oList, sOpen))
        oClose = oFile.token_at(getattr(oList, sClose))
        if oOpen is None or oClose is None or id(oOpen) not in dIndex or not ends_line(lAll, dIndex[id(oOpen)]):
            continue
        oOpenLine = dLineFirst.get(id(oOpen))
        if oOpenLine is None or id(oOpenLine) not in dLines:
            continue
        # The level the line of the opening bracket has, or will have: that of sv_indent_001 for a line that starts an
        # item, that of an outer list for one of its elements, else the line as written
        iBase = dWanted.get(id(oOpenLine))
        if iBase is None and oOpenLine.get_indent() is not None:
            iBase = oOpenLine.get_indent() * iIndentSize
        if iBase is None:
            iBase = indent_of(dLines[id(oOpenLine)])
        if iBase is None:
            continue
        bDeeper = in_if_condition(oList) or (oList.kind.name in PATTERNS and continuous_assign(oList))
        iItems = iBase + iLevel * (2 if bDeeper else 1)
        for oItem in elements(getattr(oList, sItems)):
            oToken = oFile.token_at(oItem.getFirstToken())
            if oToken is not None and id(oToken) in dLines:
                dWanted[id(oToken)] = iItems
        if id(oClose) in dLines:
            dWanted[id(oClose)] = iBase + (iLevel if bDeeper else 0)
    return dWanted
