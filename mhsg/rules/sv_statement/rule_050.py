# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import declared_names, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

OPERATIONS = (
    "AddExpression",
    "SubtractExpression",
    "MultiplyExpression",
    "BinaryAndExpression",
    "BinaryOrExpression",
    "BinaryXorExpression",
    "LogicalAndExpression",
    "LogicalOrExpression",
    "EqualityExpression",
    "InequalityExpression",
    "LessThanExpression",
    "GreaterThanExpression",
)


class rule_050(TreeRule, structure.Rule):
    """
    This rule checks for an expression with an operator that reads signals, such as a & b, written in more than
    **maximum_uses** places of a module, 2 by default, as the STARC guide recommends (2.6.1.2): compute it once, in a
    signal of its own. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign x = a & b;
       assign y = (a & b) | c;
       assign z = (a & b) ^ d;

    **Fix**

    .. code-block:: systemverilog

       assign ab = a & b;
       assign x = ab;
       assign y = ab | c;
       assign z = ab ^ d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_uses = 2
        self.configuration.append("maximum_uses")

    def problems(self, oFile):
        setSignals = {text(o) for sKind, o in declared_names(oFile) if sKind in ("signal", "port")}
        for oModule in oFile.nodes("ModuleDeclaration"):
            dUses = {}
            for oNode in descendants(oModule):
                if oNode.kind.name not in OPERATIONS or (oNode.parent is not None and oNode.parent.kind.name in OPERATIONS):
                    continue
                if oNode.parent is not None and oNode.parent.kind.name in ("VariableDimension", "ElementSelect", "ParameterDeclaration", "ForLoopStatement"):
                    continue
                if not any(o.kind.name in ("IdentifierName", "IdentifierSelectName") and text(o.identifier) in setSignals for o in descendants(oNode)):
                    # Constants, such as Width - 1, cost no logic
                    continue
                dUses.setdefault("".join(source(oNode).split()), []).append(oNode)
            for lNodes in dUses.values():
                if len(lNodes) > int(self.maximum_uses):
                    oNode = sorted(lNodes, key=lambda o: o.getFirstToken().location.offset)[int(self.maximum_uses)]
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Compute {source(oNode)} once, in a signal: it is written {len(lNodes)} times")
