# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_018(TreeRule, naming.Rule):
    """
    This rule checks that the names of modules and ports are at most **maximum_name_length** characters long, 16 by
    default, and that no two names of a file differ only in case, as the STARC guide recommends (1.1.1.9) for the top
    level of a design, whose names other tools must handle. It checks every module, as a file does not tell which is
    the top. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module serial_receiver_with_fifo (input logic Clk, input logic clk);

    **Fix**

    .. code-block:: systemverilog

       module uart_rx (input logic clk_i);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_name_length = 16
        self.configuration.append("maximum_name_length")

    def problems(self, oFile):
        dSeen = {}
        for sKind, oName in declared_names(oFile):
            sName = text(oName)
            oToken = oFile.token_at(oName)
            if oToken is None or not sName:
                continue
            if sKind in ("module", "port") and len(sName) > int(self.maximum_name_length):
                yield Problem(oToken, f"Shorten {sName} to at most {self.maximum_name_length} characters")
            if sKind in ("module", "port", "signal", "parameter", "localparam", "instance"):
                sOther = dSeen.setdefault(sName.lower(), sName)
                if sOther != sName:
                    yield Problem(oToken, f"Rename {sName}, which differs from {sOther} only in case")
