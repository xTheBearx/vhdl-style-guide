# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_029(Rule):
    """
    This rule checks for signal assignments with more than one waveform element.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS5).

    A waveform of several elements, each after a delay, describes a sequence of values in time. Synthesis ignores the
    delays, so the hardware differs from the simulation.

    **Violation**

    .. code-block:: vhdl

       pulse <= '1', '0' after 10 ns;

    **Fix**

    .. code-block:: vhdl

       pulse <= '1';
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign one value"

    def check(self, oModel, oFile):
        bReported = False
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, model.parser.semicolon):
                bReported = False
            elif model.kind(oToken) == ("waveform", "comma") and not bReported:
                bReported = True
                self.report(oFile, iIndex, "Assign one waveform element; synthesis ignores the others and their delays")
