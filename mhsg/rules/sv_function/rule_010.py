# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks for output and inout arguments of tasks, as the STARC guide recommends (4.2.3.2) for the tasks
    that drive test stimulus. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       task automatic send(input logic [7:0] data, output logic done);

    **Fix**

    .. code-block:: systemverilog

       task automatic send(input logic [7:0] data);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oTask in oFile.nodes("TaskDeclaration"):
            oPorts = oTask.prototype.portList
            for oPort in elements(oPorts.ports) if oPorts is not None else []:
                if oPort.kind.name == "FunctionPort" and text(oPort.direction) in ("output", "inout") and oPort.declarator is not None:
                    oToken = oFile.token_at(oPort.declarator.name)
                    if oToken is not None:
                        yield Problem(
                            oToken,
                            f"Do not give the task {text(oTask.prototype.name.getLastToken())} the {text(oPort.direction)} {text(oPort.declarator.name)}",
                        )
