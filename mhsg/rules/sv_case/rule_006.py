# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks that the labels of case items are constants, not signals, as the STARC guide asks (2.8.5.3). It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (sel)
           other: y = a;
           default: y = b;
       endcase

    **Fix**

    .. code-block:: systemverilog

       case (sel)
           2'd1: y = a;
           default: y = b;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setSignals = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("signal", "port")}
        for oItem in oFile.nodes("StandardCaseItem"):
            for oExpression in elements(oItem.expressions):
                for oNode in [oExpression, *descendants(oExpression)]:
                    if oNode.kind.name in ("IdentifierName", "IdentifierSelectName") and text(oNode.identifier) in setSignals:
                        oToken = oFile.token_at(oNode.identifier)
                        if oToken is not None:
                            yield Problem(oToken, f"Use a constant as the case label, not {text(oNode.identifier)}")
