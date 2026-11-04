# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")
PROCEDURAL = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock", "InitialBlock")


class rule_018(TreeRule, structure.Rule):
    """
    This rule checks that a signal is assigned in one procedural block only, one always or initial block, as the
    STARC guide asks (4.1.4.1, 4.1.4.2). Variables declared inside a block are not checked, nor blocks in different
    branches of generate constructs. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       initial reset_n = 1'b0;
       initial #100 reset_n = 1'b1;

    **Fix**

    .. code-block:: systemverilog

       initial begin
           reset_n = 1'b0;
           #100 reset_n = 1'b1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dFirst = {}
        for oBlock in oFile.nodes(*PROCEDURAL):
            setLocal = {text(o.name) for o in descendants(oBlock) if o.kind.name == "Declarator"}
            setBlock = set()
            for oNode in descendants(oBlock):
                if oNode.kind.name not in ASSIGNMENTS or oNode.left is None:
                    continue
                oFirst = oNode.left.getFirstToken()
                sName = text(oFirst)
                if sName in setLocal or sName in setBlock:
                    continue
                setBlock.add(sName)
                iBlock = oBlock.getFirstToken().location.offset
                if sName in dFirst and dFirst[sName][0] != iBlock and dFirst[sName][1] == region(oBlock):
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Assign {sName} in one procedural block: another block assigns it too")
                dFirst.setdefault(sName, (iBlock, region(oBlock)))


def region(oBlock):
    """Where a block is: the start of the module body, generate block or generate branch holding it."""
    oParent = oBlock.parent
    return (oParent.kind.name, oParent.getFirstToken().location.offset) if oParent is not None else None
