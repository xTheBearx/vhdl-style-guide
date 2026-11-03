# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_025(Rule):
    """
    This rule checks that combinational processes use :code:`process (all)`.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    The VHDL-2008 sensitivity list :code:`all` is always complete, so simulation and synthesis cannot disagree about it.
    Code for tools without VHDL-2008 support should disable this rule.

    **Violation**

    .. code-block:: vhdl

       process (a, b) is

    **Fix**

    .. code-block:: vhdl

       process (all) is
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use process (all)"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if isinstance(oProcess.sensitivity, list) and model.is_combinational(oProcess):
                    self.report(oFile, oProcess.index, "Use process (all) for the combinational process")
