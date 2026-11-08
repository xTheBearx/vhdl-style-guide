# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_flow
from mhsg.rules.sv_nodes import combinational_blocks, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_030(TreeRule, structure.Rule):
    """
    This rule checks that a combinational always block assigns each variable on every path before it reads it. It is
    disabled by default; the do254 rule set enables it (CP10, SS3).

    A variable read before it is assigned holds the value of the last run of the block: synthesis makes a latch, or a
    combinational loop when the variable is a signal of the module, and simulation and hardware can differ. The rule
    follows the paths through if and case statements: an if without else, or a case without a default item that is
    not a unique or priority case, may assign nothing. Variables assigned through an element, a slice or a member
    are not checked.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           if (enable) sum = a + b;
           result = sum;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           sum = '0;
           if (enable) sum = a + b;
           result = sum;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Assign the variable on every path before reading it"

    def problems(self, oFile):
        for oBlock in combinational_blocks(oFile):
            yield from read_before_assigned(
                oFile,
                oBlock.statement,
                False,
                "Assign {} on every path before reading it: the block reads the value of its last run",
            )


def read_before_assigned(oFile, oStatement, bSkipNonblocking, sMessage):
    """The problems of the variables a statement reads before every path assigns them, see sv_flow."""
    lAssigned = sv_flow.assigned(oStatement)
    setWatched = {o.name for o, bBlocking in lAssigned if bBlocking and o.whole}
    # A variable written element by element may be written whole that way, which the walk does not follow
    setWatched -= {o.name for o, _ in lAssigned if not o.whole}
    if bSkipNonblocking:
        setWatched -= {o.name for o, bBlocking in lAssigned if not bBlocking}
    for sName, oNode in sv_flow.first_reads(oStatement, setWatched).items():
        oToken = oFile.token_at(oNode.getFirstToken())
        if oToken is not None and text(oNode.getFirstToken()) == sName:
            yield Problem(oToken, sMessage.format(sName))
