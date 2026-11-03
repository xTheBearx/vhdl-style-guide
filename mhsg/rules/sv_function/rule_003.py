# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that the arguments of functions and tasks are declared with a type, as Verible's
    explicit-function-task-parameter-type rule does.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic parity(input data);

    **Fix**

    .. code-block:: systemverilog

       function automatic logic parity(input logic [7:0] data);
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oPort in oFile.nodes("FunctionPort"):
            if (oPort.dataType is None or oPort.dataType.kind.name == "ImplicitType") and oPort.declarator is not None:
                oToken = oFile.token_at(oPort.declarator.name)
                if oToken is not None:
                    yield Problem(oToken, f"Give argument {text(oPort.declarator.name)} a type")
