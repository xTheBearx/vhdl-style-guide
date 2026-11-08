# -*- coding: utf-8 -*-

from mhsg import language
from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_015 import first_if
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_025(TreeRule, structure.Rule):
    """
    This rule checks for latches with an asynchronous reset or set, an always_latch block whose first if tests a
    reset, as the STARC guide asks (2.4.1.3). Resets are told by the words of their names, as for port_028. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_latch
           if (!rst_ni) q <= 1'b0;
           else if (en) q <= d;

    **Fix**

    .. code-block:: systemverilog

       always_latch
           if (en) q <= d;
    """

    def __init__(self):
        super().__init__()
        # SystemVerilog only: it checks always_latch blocks, which Verilog-2005 does not have
        self.languages = (language.SYSTEMVERILOG,)
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysLatchBlock"):
            oIf = first_if(oBlock.statement)
            for oName in descendants(oIf.predicate) if oIf is not None else []:
                if oName.kind.name in ("IdentifierName", "IdentifierSelectName") and clock_reset_rank(text(oName.identifier)) == 1:
                    oToken = oFile.token_at(oName.identifier)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not reset the latch with {text(oName.identifier)}")
                    break
