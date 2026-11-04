# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.port.rule_028 import (
    CLOCK_WORDS,
    QUALIFIER_WORDS,
    RESET_WORDS,
    clock_reset_rank,
)
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_020(TreeRule, naming.Rule):
    """
    This rule checks the base names of clocks and resets, as the STARC guide recommends (1.1.5.2): the clocks of edge
    triggered always blocks are named with a clock word, such as clk, and their asynchronous resets with a reset
    word, such as rst, as port_028 tells them: **clock_words**, **reset_words** and **qualifier_words**. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge sample or negedge init_n) ...

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_sample or negedge rst_n) ...
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
        setDone = set()
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, lResets = clock_events(oBlock)
            for oEvent, iRank, sWhat in [(o, 0, "clock") for o in lClocks] + [(o, 1, "reset") for o in lResets]:
                oFirst = oEvent.expr.getFirstToken()
                sName = text(oFirst)
                if sName in setDone:
                    continue
                setDone.add(sName)
                if clock_reset_rank(sName, self.clock_words, self.reset_words, self.qualifier_words) != iRank:
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Name the {sWhat} {sName} with a {sWhat} word, such as {'clk' if iRank == 0 else 'rst'}")
