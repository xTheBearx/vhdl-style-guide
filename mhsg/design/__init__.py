# -*- coding: utf-8 -*-
"""
Design analysis: checks of the whole elaborated design, run with GHDL and Yosys.

project.py reads the design description, tools.py finds the tools, runner.py runs them, netlist.py reads the
netlist and maps its cells back to VHDL lines, and analysis.py runs the design rules and reports their findings.
"""
