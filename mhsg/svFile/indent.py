# -*- coding: utf-8 -*-
"""
Indent levels of SystemVerilog code, from the syntax tree.

A node's children are indented one level more than the node in two cases:

* the elements of a body list, such as the members of a module, the items of a begin-end block, the ports of a port
  list or the connections of an instance;
* the statement under a control statement, such as the statement of an if, of a loop, of an always block or of a
  case item, unless it is a begin-end block, a timing control (@(posedge clk)) or the if of an else if.

The first token of each such child is checked when it starts a line. A list whose first element is on the line of
its opening bracket is aligned rather than indented, and is not checked; nor is anything inside an expression. So are the keywords and closing brackets of a
node with a body, such as end, endmodule, else and the parenthesis closing a port list, at the level of the node.
Other tokens, such as the continuation lines of a long expression, are not checked yet.
"""

# Lists whose elements stand on their own lines, one level in
BODY_LISTS = {"members", "items", "ports", "declarations", "parameters", "connections"}
# The compilation unit holds the top level declarations, which are not indented
TOP_LEVEL = {"CompilationUnit"}
# Fields holding the statement under a control statement
STATEMENT_FIELDS = {"statement", "clause", "block"}
# Fields holding a part of a statement that starts its own line at the level of the statement, such as else
SAME_LEVEL_FIELDS = {"elseClause"}
# Statements that are not indented under a control statement
NOT_INDENTED_STATEMENTS = {
    "SequentialBlockStatement",
    "ParallelBlockStatement",
    "GenerateBlock",
    "TimingControlStatement",
    "ConstraintBlock",
}
# Statements not indented under else: the if of an else if
ELSE_IF = {"ConditionalStatement", "IfGenerate"}


def is_expression(sKind):
    """
    True for an expression: its lines after the first are continuations, even those of a list inside it, such as
    the items of an assignment pattern or of a randomize with block.
    """
    return sKind.endswith(("Expression", "Expr")) or sKind in ("ConditionalPredicate", "ArgumentList")


def is_body_field(sKind, sField, bList):
    """True for a field holding indented children."""
    if bList and sField in BODY_LISTS:
        return True
    return sField in STATEMENT_FIELDS or sField in SAME_LEVEL_FIELDS


def increment(sKind, sField, bList, sChildKind):
    """
    The indent of a child relative to its node: 0 or 1 for a child that starts an item, None for other children,
    such as the expression of an assignment, which keep the level of their node and are not checked.
    """
    if bList and sField in BODY_LISTS:
        return 0 if sKind in TOP_LEVEL else 1
    if sField in SAME_LEVEL_FIELDS:
        return 0
    if sField in STATEMENT_FIELDS:
        if sChildKind in NOT_INDENTED_STATEMENTS:
            return 0
        if sKind == "ElseClause" and sChildKind in ELSE_IF:
            return 0
        return 1
    return None


def is_closing(sKind):
    """True for a token that closes a construct, such as end, endmodule or a closing parenthesis."""
    return sKind.startswith("End") or sKind in ("CloseParenthesis", "CloseBrace", "Join", "JoinAny", "JoinNone")


def is_own_line(sKind):
    """True for the tokens of a node with a body that are checked when they start a line, such as end or else."""
    return sKind.endswith("Keyword") or is_closing(sKind)
