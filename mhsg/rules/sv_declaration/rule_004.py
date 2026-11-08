# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule, elements

# Where a variable with an initial value is a local of a subprogram, a class or a procedural block, not a signal
LOCAL_SCOPES = (
    "FunctionDeclaration",
    "TaskDeclaration",
    "ClassDeclaration",
    "AlwaysBlock",
    "AlwaysFFBlock",
    "AlwaysCombBlock",
    "AlwaysLatchBlock",
    "InitialBlock",
    "FinalBlock",
    "SequentialBlockStatement",
    "ForLoopStatement",
)


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks for initial values on signals and output ports: the declaration of a variable of a module, or of
    an output or inout port, with an initial value, such as logic q = 1'b0. Synthesis may ignore the value or turn it
    into a power-on value of the target, so simulation and hardware can start differently; reset the register instead.
    Constants, nets, whose initial value is a continuous assignment, the variables of functions, tasks, classes and
    procedural blocks, and the default values of input ports are not reported; initial blocks are reported by
    sv_statement_004. It is disabled by default; the do254 rule set enables it (SS16).

    **Violation**

    .. code-block:: systemverilog

       logic busy = 1'b0;

    **Fix**

    .. code-block:: systemverilog

       logic busy;

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) busy <= 1'b0;
           else busy <= start_i;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("DataDeclaration"):
            if any(text(o) == "const" for o in oNode.modifiers) or inside(oNode, *LOCAL_SCOPES):
                continue
            yield from initial_values(oFile, oNode.declarators)
        for oNode in oFile.nodes("ImplicitAnsiPort", "PortDeclaration"):
            if text(oNode.header.direction).strip() not in ("output", "inout"):
                continue
            lDeclarators = [oNode.declarator] if oNode.kind.name == "ImplicitAnsiPort" else elements(oNode.declarators)
            yield from initial_values(oFile, lDeclarators)


def initial_values(oFile, lDeclarators):
    for oDeclarator in elements(lDeclarators) if not isinstance(lDeclarators, list) else lDeclarators:
        if getattr(oDeclarator, "initializer", None) is None:
            continue
        oToken = oFile.token_at(oDeclarator.name)
        if oToken is not None:
            yield Problem(oToken, f"Remove the initial value of {text(oDeclarator.name)}, and reset it instead")
