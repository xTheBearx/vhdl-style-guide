# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_016(TreeRule, structure.Rule):
    """
    This rule checks that the named port connections of an instance of a module the file defines are in the order of
    the ports of the module, as the STARC guide recommends (3.1.3.1). It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       sub u_sub (.y(y), .a(a));  // sub declares a, then y

    **Fix**

    .. code-block:: systemverilog

       sub u_sub (.a(a), .y(y));
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dPorts = {}
        for oModule in oFile.nodes("ModuleDeclaration"):
            oPorts = oModule.header.ports
            lNames = (
                [
                    text(o.declarator.name).lower()
                    for o in elements(getattr(oPorts, "ports", None) or [])
                    if o.kind.name == "ImplicitAnsiPort" and o.declarator is not None
                ]
                if oPorts is not None
                else []
            )
            if lNames:
                dPorts[text(oModule.header.name)] = lNames
        for oNode in oFile.nodes("HierarchyInstantiation"):
            lPorts = dPorts.get(text(oNode.type))
            if lPorts is None:
                continue
            for oInstance in elements(oNode.instances):
                iLast = -1
                for oConnection in elements(oInstance.connections):
                    if oConnection.kind.name != "NamedPortConnection" or text(oConnection.name).lower() not in lPorts:
                        continue
                    iIndex = lPorts.index(text(oConnection.name).lower())
                    if iIndex < iLast:
                        oToken = oFile.token_at(oConnection.name)
                        if oToken is not None:
                            yield Problem(oToken, f"Connect {text(oConnection.name)} in the order of the ports of {text(oNode.type)}")
                        break
                    iLast = iIndex
