# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_018(TreeRule, structure.Rule):
    """
    This rule checks that a signal connected to a port of an instance has the name of the port, apart from prefixes
    and suffixes, so a signal keeps its name through the hierarchy. It is disabled by default; the do254 rule set
    enables it (DR9).

    A signal renamed at each level of the hierarchy is hard to follow from the top to the bottom of the design. The
    **strip_prefixes** and **strip_suffixes** options list the parts that are ignored, such as i\\_ and _o, which mark
    direction or kind; names are compared ignoring case. Only named connections of a signal by name are checked, not
    selects, expressions, .name or .* connections.

    **Violation**

    .. code-block:: systemverilog

       fifo u_fifo (
           .wr_data_i (payload)
       );

    **Fix**

    .. code-block:: systemverilog

       fifo u_fifo (
           .wr_data_i (wr_data)
       );
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Name the signal after the port"
        self.strip_prefixes = ["i_", "o_", "io_", "s_", "r_", "w_"]
        self.configuration.append("strip_prefixes")
        self.strip_suffixes = ["_i", "_o", "_io", "_ni", "_no", "_s", "_r", "_n", "_d", "_q", "_reg", "_sig"]
        self.configuration.append("strip_suffixes")

    def problems(self, oFile):
        for oInstance in oFile.nodes("HierarchicalInstance"):
            sInstance = text(oInstance.decl.name) if getattr(oInstance, "decl", None) is not None else ""
            for oConnection in elements(oInstance.connections):
                if oConnection.kind.name != "NamedPortConnection" or oConnection.expr is None:
                    continue
                oSignal = connected_name(oConnection.expr)
                if oSignal is None:
                    continue
                sPort, sSignal = text(oConnection.name), text(oSignal.identifier)
                if self.stem(sPort) != self.stem(sSignal):
                    oToken = oFile.token_at(oSignal.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Signal {sSignal} connected to port {sPort} of {sInstance} has another name")

    def stem(self, sName):
        """The name in lower case without one of the prefixes and one of the suffixes."""
        sName = sName.lower()
        for sPrefix in sorted(self.strip_prefixes, key=len, reverse=True):
            if sName.startswith(sPrefix.lower()) and len(sName) > len(sPrefix):
                sName = sName[len(sPrefix) :]
                break
        for sSuffix in sorted(self.strip_suffixes, key=len, reverse=True):
            if sName.endswith(sSuffix.lower()) and len(sName) > len(sSuffix):
                sName = sName[: -len(sSuffix)]
                break
        return sName


def connected_name(oExpression):
    """The IdentifierName a port connection connects, or None for any other expression."""
    while oExpression is not None and oExpression.kind.name in ("SimplePropertyExpr", "SimpleSequenceExpr", "ParenthesizedExpression"):
        oExpression = getattr(oExpression, "expr", None) or getattr(oExpression, "expression", None)
    if oExpression is not None and oExpression.kind.name == "IdentifierName":
        return oExpression
    return None
