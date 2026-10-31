# -*- coding: utf-8 -*-

from mhsg import violation
from mhsg.rule_group import case
from mhsg.rules import declaration_case
from mhsg.vhdlFile.extract import tokens


class consistent_interface_token_case(case.Rule):
    """
    Checks the case for generic and port identifiers.

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
        self.map_aspect_token = None
        self.clause_token = None
        self.interface_string = None

    def analyze(self, oFile):
        sKind = self.interface_string.lower()

        def is_entity_interface(oDeclaration):
            return oDeclaration.kind == sKind and oDeclaration.scope.kind == "entity"

        def is_in_architecture(iToken, oDeclarations):
            oUnit = oDeclarations.get_unit_at(iToken)
            return oUnit is not None and oUnit.kind == "architecture"

        oTokenMap = oFile.get_token_map()
        for iToken, oToken, sDeclared in declaration_case.find_inconsistent_names(oFile, is_entity_interface, is_in_architecture):
            sSolution = self.interface_string + " case mismatch:  Change " + oToken.get_value() + " to " + sDeclared
            oToi = tokens.New(iToken, oTokenMap.get_line_number_of_index(iToken), [oToken])
            oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
            oViolation.set_action({"value": sDeclared})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        dActions = oViolation.get_action()
        lTokens[0].set_value(dActions["value"])
        oViolation.set_tokens(lTokens)
