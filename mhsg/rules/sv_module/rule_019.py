# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

# System tasks that stop on wrong values when a design is elaborated or simulated; Verilog-2005 has only $finish
CHECKS = ("$error", "$fatal", "$finish")


class rule_019(TreeRule, structure.Rule):
    """
    This rule checks that a module with parameters checks their values with an assertion. It is disabled by default;
    the do254_plus rule set enables it (GENERIC).

    A parameter value outside the range a design supports, such as a width of zero, otherwise goes unnoticed until
    the hardware fails. The rule accepts any assertion in the file, an $error, $fatal or $finish, such as one in a
    generate if that tests the parameters, or a macro named like an assertion, such as the ASSERT macros of lowRISC; also in code an
    ifdef directive leaves out, such as one testing FORMAL. Local parameters are not checked.

    **Violation**

    .. code-block:: systemverilog

       module fifo #(
           parameter int Depth = 16
       ) (

    **Fix**

    .. code-block:: systemverilog

       if (Depth & (Depth - 1)) begin : g_depth_check
           $error("Depth must be a power of two");
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Check the parameters with an assertion"

    def problems(self, oFile):
        if has_check(oFile):
            return
        for oModule in oFile.nodes("ModuleDeclaration", "InterfaceDeclaration"):
            oParameter = first_parameter(oModule)
            if oParameter is not None:
                oToken = oFile.token_at(oParameter.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Check the parameters of {text(oModule.header.name)} with an assertion")


def first_parameter(oModule):
    """The first parameter declaration of a module, in its header or its body, not a localparam."""
    oPorts = oModule.header.parameters
    if oPorts is not None:
        for oNode in descendants(oPorts):
            if oNode.kind.name == "ParameterDeclaration" and text(oNode.keyword) != "localparam" and elements(oNode.declarators):
                return oNode
        return None
    for oNode in descendants(oModule):
        if oNode.kind.name == "ParameterDeclaration" and text(oNode.keyword) == "parameter":
            return oNode
    return None


def has_check(oFile):
    """
    True if a file holds an assertion, $error, $fatal or $finish, or uses a macro named like an assertion, such as ASSERT,
    also in code a conditional directive leaves out, such as ifdef FORMAL.
    """
    for oToken in oFile.lAllObjects:
        if isinstance(oToken, (parser.comment, parser.whitespace, parser.carriage_return, parser.blank_line)):
            continue
        sValue = oToken.get_value() or ""
        if sValue in CHECKS or sValue == "assert" or (sValue.startswith("`") and "assert" in sValue.lower()):
            return True
    return False
