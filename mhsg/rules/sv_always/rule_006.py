# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks that an always block holds at most one if or case statement at its top level, as the STARC
    guide asks (2.6.2.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           if (a) y = 1;
           if (b) z = 1;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           if (a) y = 1;
       end
       always_comb begin
           if (b) z = 1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            oStatement = oBlock.statement
            if oStatement is not None and oStatement.kind.name == "TimingControlStatement":
                oStatement = oStatement.statement
            if oStatement is None or oStatement.kind.name != "SequentialBlockStatement":
                continue
            lControls = [o for o in oStatement.items if o.kind.name in ("ConditionalStatement", "CaseStatement")]
            for oControl in lControls[1:]:
                oToken = oFile.token_at(oControl.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Move the statement to an always block of its own")
