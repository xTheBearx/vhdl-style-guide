# -*- coding: utf-8 -*-
"""
Base class of the design rules, which check the elaborated design instead of one file.
"""

from mhsg.design import netlist
from mhsg.lint.rule import Rule as LintRule


class Finding:
    """A problem found in the design, at a line of a VHDL file. file is None for a problem without a location."""

    def __init__(self, sFile, iLine, sMessage):
        self.file = sFile
        self.line = iLine
        self.message = sMessage


class Rule(LintRule):
    """
    A design rule runs only in design analysis, see analysis.py, on the result of GHDL and Yosys.
    Like lint rules, design rules never change the code. They do nothing when files are checked one at a time.
    Subclasses implement check_design(oContext) and return a list of Finding.
    """

    def __init__(self):
        super().__init__()
        self.design = True
        # Design rules are not lint rules of the lint group: they need the whole design, see the design group
        self.groups.remove("lint")
        self.groups.append("design")

    def analyze(self, oFile):
        """Design rules do not check single files."""

    def check_design(self, oContext):
        return []

    def locate(self, oContext, sModule, lCells, sSignal=None, bLast=False):
        """
        Returns (file, line) for a finding about cells of a module: the first cell with a known location, refined to
        the first assignment of the signal when it is given, or the last with bLast. (None, 0) if no cell has a location.
        """
        for sCell in lCells:
            oLocation = oContext.netlist.location(sModule, sCell)
            if oLocation is not None:
                return oContext.refine(oLocation, sSignal, bLast)
        return None, 0


def display_name(sName):
    """Returns a net name as written in the VHDL: without the backslash Yosys adds and in lower case."""
    return sName.lstrip("\\") if sName else sName


def module_text(sModule):
    return netlist.module_name(sModule)
