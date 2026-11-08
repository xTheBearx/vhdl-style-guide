# -*- coding: utf-8 -*-

from mhsg import top_level
from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_019(Rule):
    """
    This rule checks for buffer and inout ports.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A buffer port can be replaced by an out port and an internal signal, which every tool handles the same way.
    An inout port implies a tri-state driver and belongs only on the top level, for device pins, so the inout ports
    of the top level are not reported. The top level is the entity the design section of the configuration names
    with top; without one, in lint mode, an entity that no file of the run instantiates, nor the files given with
    --index_files or index_file_list. Outside lint mode, or for a file read from standard input, without the design
    section the top level is not known, and every inout port is reported. The ports of a component declaration are
    those of the entity the component names.

    In lint mode an entity checked without the files that instantiate it is a top level: give those files with
    --index_files, or name the top in the design section, to check the inout ports of a lower entity on its own. A
    testbench in the run instantiates the top level; name the top in the design section, so its pins are not
    reported.

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
                sUnit = port_unit(oFile.lAllObjects, iIndex)
                if sUnit is None or not top_level.is_top(oFile, sUnit, False):
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


def port_unit(lTokens, iIndex):
    """The name of the entity or component whose port clause holds the token, or None."""
    for iPrevious in range(iIndex - 1, -1, -1):
        if model.kind(lTokens[iPrevious]) in (("entity_declaration", "identifier"), ("component_declaration", "identifier")):
            return lTokens[iPrevious].get_value()
    return None
