# -*- coding: utf-8 -*-

from mhsg import parser, rule, violation
from mhsg.lint.model import kind
from mhsg.vhdlFile.extract import tokens

ASSIGNMENT_MODULES = {"concurrent_simple_signal_assignment", "concurrent_conditional_signal_assignment", "concurrent_selected_signal_assignment"}


class rule_013(rule.Rule):
    """
    This rule checks that concurrent signal assignments have a label.

    .. NOTE:: This rule is disabled by default.

    Labels make the statements easier to find in reviews and simulation.
    This rule cannot add labels, because it cannot name them.
    It is the opposite of concurrent_005, which removes labels, so enable only one of them.

    **Violation**

    .. code-block:: vhdl

       data_out <= div_data when clk_div_en = '1' else ser_if_data;

    **Fix**

    .. code-block:: vhdl

       data_out_mux : data_out <= div_data when clk_div_en = '1' else ser_if_data;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a label"
        self.phase = 1
        self.disable = True
        self.fixable = False
        self.groups.append("structure")

    def analyze(self, oFile):
        self._print_debug_message("Analyzing rule: " + self.unique_id)
        bLabel = False
        bInStatement = False
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            sModule, sName = kind(oToken)
            if sModule == "concurrent_signal_assignment_statement" and sName == "label_name":
                bLabel = True
            elif sModule in ASSIGNMENT_MODULES and not bInStatement:
                bInStatement = True
                if not bLabel:
                    iLine = oFile.get_token_map().get_line_number_of_index(iIndex)
                    oToi = tokens.New(iIndex, iLine, [oToken])
                    self.add_violation(violation.New(iLine, oToi, self.solution))
            if isinstance(oToken, parser.semicolon) and (bInStatement or bLabel):
                bLabel = False
                bInStatement = False
