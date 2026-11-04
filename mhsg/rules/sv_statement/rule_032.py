# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_032(TreeRule, structure.Rule):
    """
    This rule checks for edge events on signals other than clocks in initial blocks and tasks, such as @(posedge
    done), as the STARC guide recommends (4.1.8.4): wait for levels with wait or test them on a clock edge. Clocks
    are told by the words of their names, as for port_028. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       initial @(posedge done) $finish;

    **Fix**

    .. code-block:: systemverilog

       initial begin
           wait (done);
           $finish;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oEvent in oFile.nodes("SignalEventExpression"):
            if not text(oEvent.edge) or not inside(oEvent, "InitialBlock", "TaskDeclaration"):
                continue
            sName = text(oEvent.expr.getFirstToken())
            if clock_reset_rank(sName) != 0:
                oToken = oFile.token_at(oEvent.edge)
                if oToken is not None:
                    yield Problem(oToken, f"Wait for {sName} on a clock edge, not on its own edge")
