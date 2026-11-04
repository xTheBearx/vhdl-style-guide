# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks for edge event controls, such as @(posedge clk), in tasks, as the STARC guide asks (2.1.2.5). It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       task automatic send(input logic [7:0] d);
           @(posedge clk);
           data = d;
       endtask

    **Fix**

    Move the timing to the always block that calls the task, or use a function.

    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("TaskDeclaration"):
            for oEvent in descendants(oNode):
                if oEvent.kind.name == "SignalEventExpression" and text(oEvent.edge):
                    oToken = oFile.token_at(oEvent.edge)
                    if oToken is not None:
                        yield Problem(oToken, "Do not wait for a clock edge in a task")
