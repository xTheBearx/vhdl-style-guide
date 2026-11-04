# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_027(TreeRule, structure.Rule):
    """
    This rule checks for an if without else whose only statement is another if without else, as the STARC guide
    recommends (2.7.3.4): merge their conditions. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (valid)
           if (ready) q <= d;

    **Fix**

    .. code-block:: systemverilog

       if (valid & ready) q <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ConditionalStatement"):
            if oNode.elseClause is not None:
                continue
            oInner = oNode.statement
            while oInner is not None and oInner.kind.name == "SequentialBlockStatement":
                lItems = [o for o in oInner.items if hasattr(o, "kind")]
                oInner = lItems[0] if len(lItems) == 1 else None
            if oInner is not None and oInner.kind.name == "ConditionalStatement" and oInner.elseClause is None:
                oToken = oFile.token_at(oInner.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Merge the condition of this if with the one of the if around it")
