# -*- coding: utf-8 -*-

from mhsg import parser, token, violation
from mhsg.rule_group import structure
from mhsg.rules.reserved.rule_001 import dMap
from mhsg.vhdlFile.extract import tokens

# Tokens which can be enclosed in redundant parentheses
lEnclosedTokens = (parser.todo, parser.character_literal, parser.string_literal)

# Every reserved word of every VHDL standard
lReservedWords = {sWord for lWords in dMap.values() for sWord in lWords}

lUnaryLogicalOperators = (
    token.unary_logical_operator.and_operator,
    token.unary_logical_operator.or_operator,
    token.unary_logical_operator.nand_operator,
    token.unary_logical_operator.nor_operator,
    token.unary_logical_operator.xor_operator,
    token.unary_logical_operator.xnor_operator,
)

# A condition enclosed in parentheses is controlled by if_002
dConditionTokens = {
    token.if_statement.if_keyword: token.if_statement.then_keyword,
    token.if_statement.elsif_keyword: token.if_statement.then_keyword,
    token.iteration_scheme.while_keyword: token.loop_statement.loop_keyword,
}


class rule_001(structure.Rule):
    """
    This rule checks for parentheses which enclose a single name or literal in an expression.
    Such parentheses do not change the meaning of the expression.

    Parentheses are not reported when they:

    * belong to a function call, an index, a type conversion or a qualified expression
    * follow a unary reduction operator, as in **and(a)**
    * enclose an entire **if**, **elsif** or **while** condition. Rule :ref:`if_002` controls the parentheses around **if** conditions.

    .. NOTE:: This rule is disabled by default.

    **Violation**

    .. code-block:: vhdl

       if (sync_reset) = '1' then
         a <= (b) and c;

    **Fix**

    .. code-block:: vhdl

       if sync_reset = '1' then
         a <= b and c;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove parentheses around a single name or literal."
        self.disable = True
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        lAllTokens = oFile.lAllObjects
        oTokenMap = oFile.get_token_map()
        for iOpen in oTokenMap.get_token_indexes(parser.open_parenthesis):
            # Function calls, indexes and aggregates use subclasses of open_parenthesis
            if type(lAllTokens[iOpen]) is not parser.open_parenthesis:
                continue
            iInner = next_non_whitespace(iOpen + 1, lAllTokens)
            if iInner is None or type(lAllTokens[iInner]) not in lEnclosedTokens:
                continue
            iClose = next_non_whitespace(iInner + 1, lAllTokens)
            if iClose is None or type(lAllTokens[iClose]) is not parser.close_parenthesis:
                continue
            iPrevious = previous_non_whitespace(iOpen - 1, lAllTokens)
            if iPrevious is not None and follows_name(lAllTokens[iPrevious]):
                continue
            # Reduction operators such as and(a) are commonly written like a function call
            if iPrevious is not None and isinstance(lAllTokens[iPrevious], lUnaryLogicalOperators):
                continue
            if encloses_condition(iPrevious, iClose, lAllTokens):
                continue
            iLine = oTokenMap.get_line_number_of_index(iOpen)
            oToi = tokens.New(iOpen, iLine, lAllTokens[iOpen : iClose + 1])
            oToi.set_meta_data("before", lAllTokens[iOpen - 1])
            oToi.set_meta_data("after", lAllTokens[iClose + 1] if iClose + 1 < len(lAllTokens) else None)
            lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            oViolation = violation.New(oToi.get_line_number(), oToi, self.solution)
            oViolation.set_action({"before": oToi.get_meta_data("before"), "after": oToi.get_meta_data("after")})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        dAction = oViolation.get_action()
        lNewTokens = [oToken for oToken in lTokens[1:-1] if not isinstance(oToken, parser.whitespace)]
        # Keep words apart, for example not(a) becomes not a
        if needs_space(dAction["before"]):
            lNewTokens.insert(0, parser.whitespace(" "))
        if needs_space(dAction["after"]):
            lNewTokens.append(parser.whitespace(" "))
        oViolation.set_tokens(lNewTokens)


def follows_name(oToken):
    """
    A parenthesis directly after a name, literal or closing parenthesis belongs to a function call, an index,
    a qualified expression or an attribute, so it is not redundant.
    Operators, reserved words, commas and opening parentheses can be followed by redundant parentheses.
    """
    sValue = oToken.get_value()
    if sValue is None or len(sValue) == 0:
        return False
    if sValue.lower() in lReservedWords:
        return False
    return sValue[-1].isalnum() or sValue[-1] in "_)'\""


def needs_space(oToken):
    if oToken is None or isinstance(oToken, (parser.whitespace, parser.carriage_return)):
        return False
    sValue = oToken.get_value()
    return sValue is not None and len(sValue) > 0 and (sValue[-1].isalnum() or sValue[0].isalnum() or sValue[-1] == "_")


def next_non_whitespace(iIndex, lAllTokens):
    for iToken in range(iIndex, len(lAllTokens)):
        if isinstance(lAllTokens[iToken], (parser.carriage_return, parser.blank_line, parser.comment)):
            return None
        if not isinstance(lAllTokens[iToken], parser.whitespace):
            return iToken
    return None


def previous_non_whitespace(iIndex, lAllTokens):
    for iToken in range(iIndex, -1, -1):
        if not isinstance(lAllTokens[iToken], (parser.whitespace, parser.carriage_return, parser.blank_line, parser.comment)):
            return iToken
    return None


def encloses_condition(iPrevious, iClose, lAllTokens):
    if iPrevious is None:
        return False
    for oStart, oEnd in dConditionTokens.items():
        if isinstance(lAllTokens[iPrevious], oStart):
            iNext = next_non_whitespace(iClose + 1, lAllTokens)
            return iNext is not None and isinstance(lAllTokens[iNext], oEnd)
    return False
