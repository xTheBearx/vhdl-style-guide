# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_016(TreeRule, naming.Rule):
    """
    This rule checks that port names match **port_pattern**, a regular expression, by default names ending in _i, _o
    or _io, with an n before it for active low ports, and that the other signals of the module do not, so ports and
    internal signals can be told apart, as the STARC guide asks (1.1.2.5, 1.1.3.1). It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (input logic clk, output logic full);
           logic count_o;

    **Fix**

    .. code-block:: systemverilog

       module fifo (input logic clk_i, output logic full_o);
           logic count;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.port_pattern = "[a-z0-9_]+_n?(i|o|io)"
        self.configuration.append("port_pattern")

    def problems(self, oFile):
        for _, oName, bPort in module_names(oFile):
            sName = text(oName)
            oToken = oFile.token_at(oName)
            if oToken is None or not sName:
                continue
            bPortName = re.fullmatch(self.port_pattern, sName) is not None
            if bPort and not bPortName:
                yield Problem(oToken, f"Name the port {sName} like a port, matching {self.port_pattern}")
            elif not bPort and bPortName:
                yield Problem(oToken, f"Name the signal {sName} unlike a port, not matching {self.port_pattern}")


SCOPES = ("FunctionDeclaration", "TaskDeclaration", "ClassDeclaration", "PackageDeclaration", "InterfaceDeclaration")


def in_module(oNode):
    """True for a declaration of a module, not of a function, task, class, package or interface."""
    oParent = oNode.parent
    while oParent is not None:
        if oParent.kind.name in SCOPES:
            return False
        if oParent.kind.name == "ModuleDeclaration":
            return True
        oParent = oParent.parent
    return False


def module_names(oFile):
    """(node, name token, whether a port) of the ports and signals of the modules of a file."""
    for oNode in oFile.nodes("ImplicitAnsiPort"):
        if oNode.declarator is not None and in_module(oNode):
            yield oNode, oNode.declarator.name, True
    for oNode in oFile.nodes("PortDeclaration"):
        if in_module(oNode):
            for oDeclarator in elements(oNode.declarators):
                yield oNode, oDeclarator.name, True
    for oNode in oFile.nodes("DataDeclaration", "NetDeclaration"):
        if in_module(oNode):
            for oDeclarator in elements(oNode.declarators):
                yield oNode, oDeclarator.name, False
