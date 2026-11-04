# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks that a module has at most **maximum_ports** ports, 500 by default, as the STARC guide recommends
    (1.6.4.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module core (/* 640 ports */);

    **Fix**

    Split the module into blocks with fewer ports.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_ports = 500
        self.configuration.append("maximum_ports")

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            oPorts = oModule.header.ports
            iPorts = 0
            for oPort in elements(getattr(oPorts, "ports", None) or []) if oPorts is not None else []:
                iPorts += 1 if oPort.kind.name == "ImplicitAnsiPort" else 0
            iPorts += sum(len(list(elements(o.declarators))) for o in descendants(oModule) if o.kind.name == "PortDeclaration")
            if iPorts > int(self.maximum_ports):
                oToken = oFile.token_at(oModule.header.name)
                if oToken is not None:
                    yield Problem(oToken, f"Split the module: it has {iPorts} ports, more than {self.maximum_ports}")
