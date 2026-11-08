# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_flow
from mhsg.rules.sv_nodes import combinational_blocks, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

LOOP_HEADERS = ("AssignmentExpression",) + tuple(sv_flow.COMPOUND) + tuple(sv_flow.STEPS)


class rule_032(TreeRule, structure.Rule):
    """
    This rule checks that a combinational always block gives every signal it assigns in if, case and loop statements
    a default value at its start. It is disabled by default; the do254_plus rule set enables it (DEFAULT).

    A default assignment before the if and case statements makes sure every path assigns the signal, so no latch can be
    inferred, and shows the value of the signal when no branch changes it. Variables declared in the block, and loop
    variables, are not checked.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           case (state_q)
               Idle:    state_d = Start;
               default: state_d = Idle;
           endcase
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           state_d = state_q;
           case (state_q)
               Idle:    state_d = Start;
               default: state_d = Idle;
           endcase
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Assign a default value at the start of the block"

    def problems(self, oFile):
        for oBlock in combinational_blocks(oFile):
            oStatement = oBlock.statement
            if oStatement is not None and oStatement.kind.name == "TimingControlStatement":
                oStatement = oStatement.statement
            if oStatement is None or oStatement.kind.name != "SequentialBlockStatement":
                continue
            setLocal = local_names(oStatement)
            setDefaults = set()
            setDone = set()
            for oItem in oStatement.items:
                if not hasattr(oItem, "kind") or oItem.kind.name == "DataDeclaration":
                    continue
                if oItem.kind.name == "ExpressionStatement":
                    for oTarget, _ in sv_flow.assigned(oItem):
                        setDefaults.add(oTarget.name if oTarget.whole else source(oTarget.node))
                    continue
                for oTarget, _ in sv_flow.assigned(oItem):
                    if oTarget.name in setLocal or oTarget.name in setDefaults or oTarget.name in setDone:
                        continue
                    if not oTarget.whole and source(oTarget.node) in setDefaults:
                        continue
                    setDone.add(oTarget.name)
                    oToken = oFile.token_at(oTarget.node.getFirstToken())
                    if oToken is not None and text(oTarget.node.getFirstToken()) == oTarget.name:
                        yield Problem(oToken, f"Give {oTarget.name} a default value at the start of the block")


def local_names(oStatement):
    """The variables declared in a block and its loops, and the variables loop headers assign."""
    setReturn = set()
    for oNode in descendants(oStatement):
        sKind = oNode.kind.name
        if sKind == "DataDeclaration":
            setReturn.update(text(o.name) for o in elements(oNode.declarators))
        elif sKind == "ForVariableDeclaration":
            setReturn.add(text(oNode.declarator.name))
        elif sKind in sv_flow.LOOPS:
            for oChild in oNode:
                if hasattr(oChild, "kind") and oChild.kind.name in LOOP_HEADERS and oChild is not getattr(oNode, "statement", None):
                    setReturn.update(o.name for o, _ in sv_flow.assigned_by(oChild))
    return setReturn
