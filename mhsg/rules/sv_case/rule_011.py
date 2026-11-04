# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_011(TreeRule, structure.Rule):
    """
    This rule checks the size of the table a case statement makes: at most **maximum_table_inputs** selector bits, 20
    by default, **maximum_table_outputs** bits assigned, 12 by default, and **maximum_table_bits** of both, 32 by
    default, as the STARC guide recommends (2.8.2.1). The widths come from slang's elaboration of the file. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (opcode)  // 24 bits, assigning 16 bits

    **Fix**

    Split the table into smaller case statements.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_table_inputs = 20
        self.configuration.append("maximum_table_inputs")
        self.maximum_table_outputs = 12
        self.configuration.append("maximum_table_outputs")
        self.maximum_table_bits = 32
        self.configuration.append("maximum_table_bits")

    def problems(self, oFile):
        lFound = []
        for oCase in sv_types.case_statements(oFile):
            iInputs = sv_types.width(oCase.expr) or 0
            dOutputs = {}
            for oAssignment in sv_types.assignments(oCase):
                dOutputs[sv_types.text(oAssignment.left)] = sv_types.width(oAssignment.left) or 0
            iOutputs = sum(dOutputs.values())
            if iInputs > int(self.maximum_table_inputs) or iOutputs > int(self.maximum_table_outputs) or iInputs + iOutputs > int(self.maximum_table_bits):
                lFound.append((oCase.expr, f"Split the case table: {iInputs} input and {iOutputs} output bits"))
        return sv_types.problems(oFile, lFound)
