# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import integer_of, text
from mhsg.rules.sv_statement.rule_044 import loop_variables
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

RELATIONAL = (
    "EqualityExpression",
    "InequalityExpression",
    "LessThanExpression",
    "LessThanEqualExpression",
    "GreaterThanExpression",
    "GreaterThanEqualExpression",
)
LOGIC = ("LogicalAndExpression", "LogicalOrExpression", "BinaryAndExpression", "BinaryOrExpression", "BinaryXorExpression")


class rule_045(TreeRule, structure.Rule):
    """
    This rule checks that for loops with comparisons or logic in them run at most **maximum_iterations** times, 10 by
    default, as the STARC guide recommends (2.9.2.3). Only loops whose bounds are numbers are checked. It is disabled
    by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0; i < 32; i++) if (a[i] == b[i]) ...

    **Fix**

    Compare the vectors as a whole, or split the loop.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_iterations = 10
        self.configuration.append("maximum_iterations")

    def problems(self, oFile):
        for oLoop in oFile.nodes("ForLoopStatement"):
            iCount = iterations(oLoop)
            if iCount is None or iCount <= int(self.maximum_iterations):
                continue
            if any(o.kind.name in RELATIONAL + LOGIC for o in descendants(oLoop.statement)):
                oToken = oFile.token_at(oLoop.forKeyword)
                if oToken is not None:
                    yield Problem(oToken, f"Run the loop at most {self.maximum_iterations} times: it runs {iCount}")


def iterations(oLoop):
    """The number of iterations of a loop such as for (i = 0; i < 8; i++), or None if its bounds are not numbers."""
    lInitializers = list(elements(oLoop.initializers))
    if len(lInitializers) != 1 or oLoop.stopExpr is None:
        return None
    oInitializer = lInitializers[0]
    oStart = (
        oInitializer.declarator.initializer.expr
        if oInitializer.kind.name == "ForVariableDeclaration" and oInitializer.declarator is not None and oInitializer.declarator.initializer is not None
        else getattr(oInitializer, "right", None)
    )
    iStart = integer_of(oStart) if oStart is not None else None
    oStop = oLoop.stopExpr
    if (
        iStart is None
        or oStop.kind.name not in ("LessThanExpression", "LessThanEqualExpression")
        or text(oStop.left.getFirstToken()) not in loop_variables(oLoop)
    ):
        return None
    iEnd = integer_of(oStop.right)
    if iEnd is None:
        return None
    return iEnd - iStart + (1 if oStop.kind.name == "LessThanEqualExpression" else 0)
