# -*- coding: utf-8 -*-

from mhsg import violation
from mhsg.rule_group import case
from mhsg.rules import declaration_case
from mhsg.vhdlFile.extract import tokens


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
        oTokenMap = oFile.get_token_map()
        for iToken, oToken, sDeclared in declaration_case.find_inconsistent_names(oFile, lambda oDeclaration: oDeclaration.kind == "loop_parameter"):
            oToi = tokens.New(iToken, oTokenMap.get_line_number_of_index(iToken), [oToken])
            oToi.set_meta_data("expected", sDeclared)
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
