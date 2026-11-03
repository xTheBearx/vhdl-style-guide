# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_019(Rule):
    """
    This rule checks for buffer and inout ports.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A buffer port can be replaced by an out port and an internal signal, which every tool handles the same way.
    An inout port implies a tri-state driver and belongs only on the top level, for device pins.

    **Violation**

    .. code-block:: vhdl

       port (
         count : buffer unsigned(3 downto 0)
       );

    **Fix**

    .. code-block:: vhdl

       port (
         count : out unsigned(3 downto 0)
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use in or out ports"

    def check(self, oModel, oFile):
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            if tKind == ("mode", "buffer_keyword"):
                self.report(oFile, iIndex, "Replace the buffer port with an out port and an internal signal")
            elif tKind == ("mode", "inout_keyword") and in_port_clause(oFile.lAllObjects, iIndex):
                self.report(oFile, iIndex, "Use inout ports only on the top level, for device pins")


def in_port_clause(lTokens, iIndex):
    """Returns True if the token is in a port clause, not in a subprogram parameter list."""
    for iPrevious in range(iIndex - 1, -1, -1):
        sModule = model.kind(lTokens[iPrevious])[0]
        if sModule == "port_clause":
            return True
        if sModule in ("procedure_specification", "function_specification"):
            return False
    return False
