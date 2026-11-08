# -*- coding: utf-8 -*-
"""
The top level of a design, for rules that treat it differently from the units it instantiates, such as lint_019 and
sv_module_020, which allow inout ports on the top level only, for the pins of the device.

A top level is:

* the unit the design section of the configuration names with top, when it names one;
* otherwise, in lint mode, a unit that no file of the run instantiates, nor the files given with --index_files or
  index_file_list;
* otherwise none: without the design section and the files of the run, the top level is not known.
"""


def is_top(oFile, sName, bVerilog):
    """
    Whether the entity or module sName is a top level of the design. A Verilog or SystemVerilog name (bVerilog) is
    matched as written, a VHDL name in any case.
    """
    oConfiguration = getattr(oFile, "configuration", None)
    sTop = design_top(oConfiguration)
    if sTop is not None:
        return sName == sTop if bVerilog else sName.lower() == sTop.lower()
    setVhdl, setVerilog = instantiated(oConfiguration)
    if setVhdl is None:
        return False
    if bVerilog:
        return sName not in setVerilog and sName.lower() not in setVhdl
    return sName.lower() not in setVhdl and sName.lower() not in {s.lower() for s in setVerilog}


def design_top(oConfiguration):
    """The top the design section of the configuration names, or None."""
    dDesign = (getattr(oConfiguration, "dConfig", None) or {}).get("design")
    sTop = dDesign.get("top") if isinstance(dDesign, dict) else None
    return str(sTop) if sTop else None


def instantiated(oConfiguration):
    """
    The names of the units the files of the run instantiate, as (VHDL names in lower case, Verilog and SystemVerilog
    names), or (None, None) when the run is not known: outside lint mode, or for a file read from standard input.
    """
    setVhdl = getattr(oConfiguration, "project_instantiated_units", None)
    if setVhdl is None:
        return None, None
    # Every entry of the compiled Verilog and SystemVerilog files holds the modules the run instantiates, see svFile/project.py
    dProject = getattr(oConfiguration, "sv_lint_project", None) or {}
    dEntry = next(iter(dProject.values()), None) or {}
    return setVhdl, dEntry.get("instances") or set()
