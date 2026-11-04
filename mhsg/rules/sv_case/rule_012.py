# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source, text, vector_literal
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_012(TreeRule, structure.Rule):
    """
    This rule checks that the wildcard bits, x, z or ?, of the items of a casex or casez statement are next to each
    other, not scattered between other bits, as the STARC guide recommends (2.8.4.4). It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       casez (sel)
           4'b1?0?: y = a;

    **Fix**

    .. code-block:: systemverilog

       casez (sel)
           4'b10??: y = a;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            if text(oCase.caseKeyword) not in ("casex", "casez"):
                continue
            for oItem in elements(oCase.items):
                for oExpression in elements(getattr(oItem, "expressions", None) or []):
                    oLiteral = vector_literal(oExpression) if oExpression.kind.name == "IntegerVectorExpression" else None
                    if oLiteral is None:
                        continue
                    sMask = "".join("w" if c in "xXzZ?" else "d" for c in oLiteral.digits)
                    if sMask.strip("d").count("d") > 0 and "w" in sMask:
                        oToken = oFile.token_at(oExpression.getFirstToken())
                        if oToken is not None:
                            yield Problem(oToken, f"Keep the wildcard bits of {source(oExpression)} together")
