# -*- coding: utf-8 -*-
"""
The expressions of a SystemVerilog file with their types, from slang's elaboration of the file on its own, for the
rules on widths. Each module is elaborated once for each time the file instantiates it, so the rules report a place
once.
"""

import re

from pyslang import ast  # pylint: disable=import-error

from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem

KINDS = ("BinaryOp", "UnaryOp", "ConditionalOp", "Conditional", "Conversion", "Assignment", "Case")
# The conversions slang adds to an operand, which give it the width of its context
IMPLICIT = ("Implicit", "Propagated")


def expressions(oFile):
    """The expressions and conditional statements of a file, built once: [AST node], kept with their compilation."""
    oCache = getattr(oFile, "_typed_expressions", None)
    if oCache is None:
        oCompilation = ast.Compilation()
        oCompilation.addSyntaxTree(oFile.syntax_tree)
        lNodes = []

        def visit(oNode):
            if oNode.kind.name in KINDS:
                lNodes.append(oNode)
            return True

        oCompilation.getRoot().visit(visit)
        oCache = (oCompilation, lNodes)
        oFile._typed_expressions = oCache  # pylint: disable=protected-access
    return oCache[1]


def nodes(oFile, *lKinds):
    return [o for o in expressions(oFile) if o.kind.name in lKinds]


def own(oExpression):
    """An operand without the conversions slang adds to give it the width of its context."""
    while oExpression is not None and oExpression.kind.name == "Conversion" and str(oExpression.conversionKind).split(".")[-1] in IMPLICIT:
        oExpression = oExpression.operand
    return oExpression


def width(oExpression):
    """
    The width of an operand in bits, as written, or None. A choice between constants, such as c ? 2 : 4, has the
    width its values need, which slang computes, rather than the 32 bits of its numbers.
    """
    oOwn = own(oExpression)
    if oOwn is None:
        return None
    if oOwn.kind.name == "ConditionalOp" and constant(oOwn.left) and constant(oOwn.right):
        return getattr(oOwn, "effectiveWidth", None)
    oType = getattr(oOwn, "type", None)
    return getattr(oType, "bitWidth", None) if oType is not None else None


def constant(oExpression):
    """True for an operand slang can compute, such as a parameter, a sized number or Width - 1."""
    oOwn = own(oExpression)
    return oOwn is not None and getattr(oOwn, "constant", None) is not None


def call(oExpression):
    """True for a call of a function or a system function, such as $test$plusargs."""
    oOwn = own(oExpression)
    return oOwn is not None and oOwn.kind.name == "Call"


def unsized(oExpression):
    """True for a number without a width, such as 3, or a fill such as '0."""
    oOwn = own(oExpression)
    return oOwn is not None and (bool(getattr(oOwn, "isUnsizedInteger", False)) or oOwn.kind.name == "UnbasedUnsizedIntegerLiteral")


def value(oExpression):
    """The integer value of a constant operand, or None."""
    oConstant = getattr(own(oExpression), "constant", None)
    if oConstant is None:
        return None
    oMatch = re.fullmatch(r"(?:\d+'s?[dD])?(\d+)", str(oConstant).strip())
    return int(oMatch.group(1)) if oMatch else None


def operator(oNode):
    """The name of the operator of a unary or binary operation, such as LogicalAnd."""
    return str(oNode.op).split(".")[-1]


def first_syntax(oNode):
    """The syntax node of an AST node, or of its first operand when slang made it, as for a conversion."""
    while oNode is not None and getattr(oNode, "syntax", None) is None:
        oNode = getattr(oNode, "operand", None)
    return oNode.syntax if oNode is not None else None


def text(oNode):
    """The code of an expression, on one line."""
    oSyntax = first_syntax(oNode)
    return " ".join(source(oSyntax).split()) if oSyntax is not None else "the expression"


def problems(oFile, lFound):
    """Problems for (AST node, message) pairs, once for each place and message, as a module may be elaborated twice."""
    setDone = set()
    for oNode, sMessage in lFound:
        oSyntax = first_syntax(oNode)
        oToken = oFile.token_at(oSyntax.getFirstToken()) if oSyntax is not None else None
        if oToken is None or (id(oToken), sMessage) in setDone:
            continue
        setDone.add((id(oToken), sMessage))
        yield Problem(oToken, sMessage)


def has_unsized(oExpression):
    """True for an operand that is or holds a number without a width, such as rd_addr + 4, whose width it sets."""
    oOwn = own(oExpression)
    if oOwn is None:
        return False
    if unsized(oOwn):
        return True
    lOperands = [getattr(oOwn, s, None) for s in ("left", "right", "operand")]
    return any(o is not None and has_unsized(o) for o in lOperands)


def case_statements(oFile):
    """The case statements of a file."""
    return nodes(oFile, "Case")


def assignments(oStatement):
    """The assignments under a statement."""
    lReturn = []

    def visit(oNode):
        if oNode.kind.name == "Assignment":
            lReturn.append(oNode)
        return True

    oStatement.visit(visit)
    return lReturn
