# -*- coding: utf-8 -*-

from mhsg import token, violation
from mhsg.rule_group import case
from mhsg.rules import declaration_case
from mhsg.vhdlFile.extract import tokens


class consistent_subprogram_parameter_token_case(case.Rule):
    """
    Checks the case for formal parameter interface identifiers.

    Parameters
    ----------

    name : string
       The group the rule belongs to.

    identifier : string
       unique identifier.  Usually in the form of 00N.

    lTokens: list of token type objects
       token type to apply the case check against
    """

    def __init__(self):
        super().__init__()
        self.subphase = 2
        self.configuration_documentation_link = None
        self.subprogram_token = None
        self.start_token = None
        self.end_token = token.subprogram_body.end_keyword

    def analyze(self, oFile):
        sDesignatorKind = "procedure" if self.subprogram_token == token.procedure_specification else "function"

        def is_parameter(oDeclaration):
            return oDeclaration.kind == "parameter" and oDeclaration.scope.kind == "subprogram" and oDeclaration.scope.designator_kind == sDesignatorKind

        oTokenMap = oFile.get_token_map()
        for iToken, oToken, sDeclared in declaration_case.find_inconsistent_names(oFile, is_parameter):
            sSolution = "Parameter case mismatch:  Change " + oToken.get_value() + " to " + sDeclared
            oToi = tokens.New(iToken, oTokenMap.get_line_number_of_index(iToken), [oToken])
            oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
            oViolation.set_action({"value": sDeclared})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        dActions = oViolation.get_action()
        lTokens[0].set_value(dActions["value"])
        oViolation.set_tokens(lTokens)
