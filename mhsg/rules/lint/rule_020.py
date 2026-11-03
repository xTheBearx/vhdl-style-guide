# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_020(Rule):
    """
    This rule checks how processes use clock edges.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A clock edge should be written with :code:`rising_edge` or :code:`falling_edge`, which ignore transitions from metavalues,
    rather than with :code:`clk'event`. A process should use one edge of one clock; registers on other clocks or edges belong in a process of their own.

    **Violation**

    .. code-block:: vhdl

       if clk'event and clk = '1' then

    **Fix**

    .. code-block:: vhdl

       if rising_edge(clk) then
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use one rising_edge or falling_edge per process"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                lEdges = []
                for oStatement in model.walk(oProcess.statements):
                    if not isinstance(oStatement, model.If):
                        continue
                    for tBranch in oStatement.branches:
                        for sClock, sEdge in model.edges(tBranch[0] or []):
                            if sEdge == "event":
                                self.report(oFile, tBranch[3], f"Use rising_edge({sClock}) or falling_edge({sClock}) instead of {sClock}'event")
                            lEdges.append((sClock, sEdge))
                lDistinct = sorted({(c, "rising" if e == "event" else e) for c, e in lEdges})
                if len(lDistinct) > 1:
                    sEdges = ", ".join(f"{e} edge of {c}" for c, e in lDistinct)
                    self.report(oFile, oProcess.index, f"The process uses more than one clock edge ({sEdges}); use one process for each")
