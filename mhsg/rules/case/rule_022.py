# -*- coding: utf-8 -*-

from mhsg import rule, violation
from mhsg.lint.model import kind
from mhsg.vhdlFile.extract import tokens


class rule_022(rule.Rule):
    """
    This rule checks that case statements have a label.

    .. NOTE:: This rule is disabled by default.

    Labels make the statements easier to find in reviews and simulation.
    This rule cannot add labels, because it cannot name them.
    It is the opposite of case_019, which removes labels, so enable only one of them.

    **Violation**

    .. code-block:: vhdl

       case address is

    **Fix**

    .. code-block:: vhdl

       address_decode : case address is
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
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = kind(oToken)
            if tKind == ("case_statement", "case_label"):
                bLabel = True
            elif tKind == ("case_statement", "case_keyword"):
                if not bLabel:
                    iLine = oFile.get_token_map().get_line_number_of_index(iIndex)
                    self.add_violation(violation.New(iLine, tokens.New(iIndex, iLine, [oToken]), self.solution))
                bLabel = False
