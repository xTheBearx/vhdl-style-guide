# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_019(TreeRule, structure.Rule):
    """
    This rule checks for branches of an if, else if chain with the same statements, as the STARC guide recommends
    (2.7.2.1): merge their conditions. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (a) y = 1'b1;
       else if (b) y = 1'b1;
       else y = 1'b0;

    **Fix**

    .. code-block:: systemverilog

       if (a || b) y = 1'b1;
       else y = 1'b0;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oHead in chain_heads(oFile):
            dSeen = {}
            for _, oStatement in chain(oHead):
                sBody = compact(oStatement)
                if sBody in dSeen:
                    oToken = oFile.token_at(oStatement.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Merge this branch with the one on line {dSeen[sBody]}, which has the same statements")
                else:
                    dSeen[sBody] = oFile.line_of(oStatement.getFirstToken().location.offset)


def chain(oIf):
    """(predicate, statement) of each if of an if, else if chain, then (None, statement) for its final else."""
    lReturn = []
    while oIf is not None:
        lReturn.append((oIf.predicate, oIf.statement))
        oElse = oIf.elseClause.clause if oIf.elseClause is not None else None
        if oElse is not None and oElse.kind.name == "ConditionalStatement":
            oIf = oElse
        else:
            if oElse is not None:
                lReturn.append((None, oElse))
            oIf = None
    return lReturn


def chain_heads(oFile):
    """The if statements that are not the else if of another."""
    return [o for o in oFile.nodes("ConditionalStatement") if o.parent is None or o.parent.kind.name != "ElseClause"]


def compact(oNode):
    """The text of a node without white space."""
    return "".join(source(oNode).split())
