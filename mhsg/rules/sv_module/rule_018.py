# -*- coding: utf-8 -*-

import os

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements
from mhsg.svFile import project


class rule_018(TreeRule, structure.Rule):
    """
    This rule checks that a signal connected to a port of an instance has the name of the port, apart from prefixes
    and suffixes, so a signal keeps its name through the hierarchy. It is disabled by default; the do254 rule set
    enables it (DR9).

    A signal renamed at each level of the hierarchy is hard to follow from the top to the bottom of the design. The
    **strip_prefixes** and **strip_suffixes** options list the parts that are ignored, such as i\\_ and _o, which mark
    direction or kind; one prefix and one suffix, the longest that fits, are removed and the names compared ignoring
    case, as lint_040 does for VHDL. The default suffixes include those of port names written by direction, the
    names sv_naming_016 asks for: _i, _o and _io, with _n or n before them for active low ports, so tick_o matches
    tick and tick_i, and rst_n_i or rst_ni matches rst_n. Only named connections of a signal by name are checked, not
    selects, expressions, .name or .* connections.

    The ports of a module instantiated more than once are not checked: each instance connects its own signals, which
    cannot all have the names of the ports. In lint mode the instances of all the files of the run are counted,
    otherwise those of the file; an instance array or an instance in a loop generate counts as more than one. lint_040
    does the same for VHDL.

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
        self.strip_suffixes = ["_i", "_o", "_io", "_ni", "_no", "_nio", "_n_i", "_n_o", "_n_io", "_s", "_r", "_n", "_d", "_q", "_reg", "_sig"]
        self.configuration.append("strip_suffixes")

    def problems(self, oFile):
        dInstances = instances(oFile)
        for oInstance in oFile.nodes("HierarchicalInstance"):
            if oInstance.parent is not None and dInstances.get(text(oInstance.parent.type), 0) > 1:
                continue
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


def instances(oFile):
    """
    {module name: number of instances}: of the files of the run when lint mode compiled the run, see
    svFile/project.py, and of the file, whichever is more.
    """
    dReturn = project.instance_counts(oFile.nodes("HierarchicalInstance"))
    dProject = getattr(getattr(oFile, "configuration", None), "sv_lint_project", None) or {}
    dEntry = dProject.get(os.path.abspath(oFile.filename)) if getattr(oFile, "filename", None) else None
    if dEntry is None and dProject:
        dEntry = next(iter(dProject.values()))
    for sModule, iCount in ((dEntry or {}).get("instances") or {}).items():
        dReturn[sModule] = max(iCount, dReturn.get(sModule, 0))
    return dReturn


def connected_name(oExpression):
    """The IdentifierName a port connection connects, or None for any other expression."""
    while oExpression is not None and oExpression.kind.name in ("SimplePropertyExpr", "SimpleSequenceExpr", "ParenthesizedExpression"):
        oExpression = getattr(oExpression, "expr", None) or getattr(oExpression, "expression", None)
    if oExpression is not None and oExpression.kind.name == "IdentifierName":
        return oExpression
    return None
