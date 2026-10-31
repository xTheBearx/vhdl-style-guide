# -*- coding: utf-8 -*-

from mhsg import parser, violation
from mhsg.rule_group import structure
from mhsg.token import (
    function_specification,
    generic_clause,
    interface_function_specification,
    interface_list,
    interface_procedure_specification,
    port_clause,
    procedure_specification,
)
from mhsg.vhdlFile.extract import tokens

# The closing parentheses of generic lists, port lists and parameter lists
lCloseParentheses = (
    generic_clause.close_parenthesis,
    port_clause.close_parenthesis,
    procedure_specification.close_parenthesis,
    function_specification.close_parenthesis,
    interface_procedure_specification.close_parenthesis,
    interface_function_specification.close_parenthesis,
)

lSkipTokens = (parser.whitespace, parser.carriage_return, parser.blank_line, parser.comment)


class rule_001(structure.Rule):
    """
    This rule checks for the optional semicolon after the last element of a generic, port or parameter list.
    VHDL-2019 allows this semicolon; earlier versions of VHDL do not.

    |configuring_optional_items_link|

    .. NOTE:: This rule is disabled by default.
       Its default action is :code:`remove`, which keeps the code valid for tools that do not support VHDL-2019.

    **Violation**

    .. code-block:: vhdl

       port (
         a : in    std_logic;
         b : out   std_logic;
       );

    **Fix**

    .. code-block:: vhdl

       port (
         a : in    std_logic;
         b : out   std_logic
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "trailing semicolon in interface list."
        self.disable = True
        self.action = "remove"
        self.configuration.append("action")
        self.groups.append("structure::optional")
        self.configuration_documentation_link = "configuring_optional_items_link"

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        lAllTokens = oFile.lAllObjects
        oTokenMap = oFile.get_token_map()
        for oCloseParenthesis in lCloseParentheses:
            for iClose in oTokenMap.get_token_indexes(oCloseParenthesis):
                iLast = previous_token(iClose - 1, lAllTokens)
                # An empty list has nothing to end
                if iLast is None or isinstance(lAllTokens[iLast], parser.open_parenthesis):
                    continue
                oToi = tokens.New(iLast, oTokenMap.get_line_number_of_index(iLast), [lAllTokens[iLast]])
                oToi.set_meta_data("has_semicolon", isinstance(lAllTokens[iLast], interface_list.semicolon))
                lReturn.append(oToi)
        return sorted(lReturn, key=lambda oToi: oToi.get_start_index())

    def _analyze(self, lToi):
        for oToi in lToi:
            bHasSemicolon = oToi.get_meta_data("has_semicolon")
            if self.action == "remove" and bHasSemicolon:
                oViolation = violation.New(oToi.get_line_number(), oToi, "Remove " + self.solution)
            elif self.action == "add" and not bHasSemicolon:
                oViolation = violation.New(oToi.get_line_number(), oToi, "Add " + self.solution)
            else:
                continue
            oViolation.set_action(self.action)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        if oViolation.get_action() == "remove":
            oViolation.set_tokens([])
        else:
            oViolation.set_tokens([lTokens[0], interface_list.semicolon()])


def previous_token(iIndex, lAllTokens):
    for iToken in range(iIndex, -1, -1):
        if not isinstance(lAllTokens[iToken], lSkipTokens):
            return iToken
    return None
