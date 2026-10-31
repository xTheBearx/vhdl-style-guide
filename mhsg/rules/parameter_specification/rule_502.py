# -*- coding: utf-8 -*-

from mhsg import parser, token, violation
from mhsg.rule_group import case
from mhsg.vhdlFile.extract import tokens

# Tokens which open and close the scope of a loop or generate parameter
dScopeTokens = {
    token.iteration_scheme.for_keyword: (token.loop_statement.loop_keyword, token.loop_statement.end_loop_keyword),
    token.for_generate_statement.for_keyword: (token.for_generate_statement.generate_keyword, token.for_generate_statement.end_generate_keyword),
}

lIgnoreTokens = [parser.comment, parser.keyword, parser.character_literal, parser.string_literal, parser.whitespace, parser.carriage_return]


class rule_502(case.Rule):
    """
    This rule checks for consistent capitalization of loop and generate parameter names.

    **Violation**

    .. code-block:: vhdl

       GEN_LABEL : for I in t_index_range generate
         DATA(i) <= INPUT(i);
       end generate GEN_LABEL;

    **Fix**

    .. code-block:: vhdl

       GEN_LABEL : for I in t_index_range generate
         DATA(I) <= INPUT(I);
       end generate GEN_LABEL;
    """

    def __init__(self):
        super().__init__()
        self.subphase = 2
        self.groups.append("case::name")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        lAllTokens = oFile.lAllObjects
        oTokenMap = oFile.get_token_map()
        for iIndex, oToken in enumerate(lAllTokens):
            if not isinstance(oToken, token.parameter_specification.identifier):
                continue
            tScope = get_scope_tokens(iIndex, lAllTokens)
            if tScope is None:
                continue
            sParameter = oToken.get_value()
            for iName in get_references(iIndex, sParameter, tScope, lAllTokens):
                if lAllTokens[iName].get_value() != sParameter:
                    oToi = tokens.New(iName, oTokenMap.get_line_number_of_index(iName), [lAllTokens[iName]])
                    oToi.set_meta_data("expected", sParameter)
                    lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            sExpected = oToi.get_meta_data("expected")
            sActual = oToi.get_tokens()[0].get_value()
            oViolation = violation.New(oToi.get_line_number(), oToi, f"Change {sActual} to {sExpected}")
            oViolation.set_action({"expected": sExpected})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        lTokens[0].set_value(oViolation.get_action()["expected"])
        oViolation.set_tokens(lTokens)


def get_scope_tokens(iIndex, lAllTokens):
    """
    Returns the tokens opening and closing the body of the loop or generate the parameter belongs to.
    """
    for iPrevious in range(iIndex - 1, -1, -1):
        oToken = lAllTokens[iPrevious]
        for oForKeyword, tScope in dScopeTokens.items():
            if isinstance(oToken, oForKeyword):
                return tScope
        if not isinstance(oToken, (parser.whitespace, parser.carriage_return, parser.comment)):
            return None
    return None


def get_references(iIndex, sParameter, tScope, lAllTokens):
    """
    Returns the indexes of references to the parameter within its loop or generate body.
    A nested loop or generate declaring a parameter of the same name hides it.
    """
    lReturn = []
    oOpen, oClose = tScope
    iDepth = 0
    iHidden = None
    for iCurrent in range(iIndex + 1, len(lAllTokens)):
        oToken = lAllTokens[iCurrent]
        if isinstance(oToken, oOpen):
            iDepth += 1
        elif isinstance(oToken, oClose):
            iDepth -= 1
            if iHidden is not None and iDepth < iHidden:
                iHidden = None
            if iDepth == 0:
                break
        elif isinstance(oToken, token.parameter_specification.identifier):
            if oToken.get_value().lower() == sParameter.lower() and iHidden is None:
                iHidden = iDepth + 1
        elif iHidden is None and oToken.get_value().lower() == sParameter.lower() and not isinstance(oToken, tuple(lIgnoreTokens)):
            lReturn.append(iCurrent)
    return lReturn
