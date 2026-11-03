# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants
from mhsg.vhdlFile import utils


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that sequential logic, in always_ff blocks and in always blocks clocked on an edge, uses
    nonblocking assignments (<=). Blocking assignments in the header of a for loop are allowed; with
    **waive_for_locals** set to yes, so are blocking assignments to variables declared in the block.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count_q = count_d;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count_q <= count_d;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a nonblocking assignment (<=) in sequential logic"
        self.waive_for_locals = "no"
        self.configuration.append("waive_for_locals")

    def problems(self, oFile):
        bWaive = utils.convert_yes_no_option_to_boolean(self.waive_for_locals)
        for oBlock in oFile.nodes("AlwaysFFBlock", "AlwaysBlock"):
            if oBlock.kind.name == "AlwaysBlock" and not is_clocked(oBlock):
                continue
            lNodes = list(descendants(oBlock))
            sLocals = local_variables(lNodes) if bWaive else set()
            sLoopHeaders = set()
            for oNode in lNodes:
                if oNode.kind.name == "ForLoopStatement":
                    for oPart in list(oNode.initializers) + list(oNode.steps):
                        sLoopHeaders.update(id_of(o) for o in descendants(oPart))
                        sLoopHeaders.add(id_of(oPart))
            for oNode in lNodes:
                if oNode.kind.name != "AssignmentExpression" or id_of(oNode) in sLoopHeaders:
                    continue
                if bWaive and target_name(oNode.left) in sLocals:
                    continue
                oToken = oFile.token_at(oNode.operatorToken)
                if oToken is not None:
                    yield Problem(oToken, self.solution)


def id_of(oNode):
    """Identifies a syntax node by its kind and the place of its first token, as pyslang makes new objects."""
    oFirst = oNode.getFirstToken()
    return (oNode.kind.name, oFirst.location.offset if oFirst is not None else None)


def is_clocked(oBlock):
    """True for an always block whose event control has an edge, such as @(posedge clk)."""
    oStatement = oBlock.statement
    if oStatement is None or oStatement.kind.name != "TimingControlStatement":
        return False
    return any(o.kind.name == "SignalEventExpression" and o.edge is not None and o.edge.rawText for o in descendants(oStatement.timingControl))


def local_variables(lNodes):
    sReturn = set()
    for oNode in lNodes:
        if oNode.kind.name == "DataDeclaration":
            sReturn.update(o.name.rawText for o in oNode.declarators)
        elif oNode.kind.name == "ForVariableDeclaration":
            sReturn.add(oNode.declarator.name.rawText)
    return sReturn


def target_name(oLeft):
    oFirst = oLeft.getFirstToken()
    return oFirst.rawText if oFirst is not None else ""
