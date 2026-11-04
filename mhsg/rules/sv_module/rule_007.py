# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import (
    CLOCK_WORDS,
    QUALIFIER_WORDS,
    RESET_WORDS,
    clock_reset_rank,
)
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements

KINDS = ["clock", "reset", "input", "output", "inout"]


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks the order of the ports of a module: clocks, resets, other inputs, outputs, then inout ports, as
    the STARC guide recommends (3.1.3.2). Clocks and resets are told by the words of their names, as for port_028:
    **clock_words**, **reset_words** and **qualifier_words**. It is disabled by default; the starc rule set enables
    it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (input logic data_i, input logic clk_i, output logic full_o, input logic rst_ni);

    **Fix**

    .. code-block:: systemverilog

       module fifo (input logic clk_i, input logic rst_ni, input logic data_i, output logic full_o);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.clock_words = list(CLOCK_WORDS)
        self.configuration.append("clock_words")
        self.reset_words = list(RESET_WORDS)
        self.configuration.append("reset_words")
        self.qualifier_words = list(QUALIFIER_WORDS)
        self.configuration.append("qualifier_words")

    def problems(self, oFile):
        for oList in oFile.nodes("AnsiPortList"):
            sDirection = "inout"
            iHighest = 0
            for oPort in elements(oList.ports):
                if oPort.kind.name != "ImplicitAnsiPort" or oPort.declarator is None:
                    continue
                oDirection = getattr(oPort.header, "direction", None)
                if oDirection is not None and text(oDirection):
                    sDirection = text(oDirection)
                if sDirection not in ("input", "output", "inout"):
                    continue
                sName = text(oPort.declarator.name)
                iRank = KINDS.index(sDirection)
                if sDirection == "input":
                    iRank = min(clock_reset_rank(sName, self.clock_words, self.reset_words, self.qualifier_words), 2)
                if iRank < iHighest:
                    oToken = oFile.token_at(oPort.declarator.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Move the {KINDS[iRank]} port {sName} before the {KINDS[iHighest]} ports")
                iHighest = max(iHighest, iRank)
