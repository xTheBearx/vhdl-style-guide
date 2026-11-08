# -*- coding: utf-8 -*-
"""
The language of a file, from its extension: SystemVerilog for .sv and .svh, Verilog for .v and .vh, VHDL for anything
else. svFile reads both Verilog and SystemVerilog files; Verilog files as Verilog-2005 (IEEE 1364-2005), so names
that are keywords only in SystemVerilog, such as logic, are names, and the rules that need SystemVerilog are not
applied to them.

A project that writes SystemVerilog in .v files reads them as SystemVerilog with v_files in the systemverilog section
of the configuration:

    systemverilog:
      v_files: systemverilog   # or verilog, the default
"""

import os

from mhsg import exceptions

VHDL = "vhdl"
VERILOG = "verilog"
SYSTEMVERILOG = "systemverilog"
LANGUAGES = (VHDL, VERILOG, SYSTEMVERILOG)
# The languages svFile reads
VERILOG_LANGUAGES = (VERILOG, SYSTEMVERILOG)

VERILOG_EXTENSIONS = (".v", ".vh")
SYSTEMVERILOG_EXTENSIONS = (".sv", ".svh")


def v_files(dConfig):
    """
    The language .v and .vh files are read as: v_files of the systemverilog section of a configuration dictionary,
    verilog by default. Raises a ConfigurationError for another value.
    """
    dSection = (dConfig or {}).get("systemverilog") if isinstance(dConfig, dict) else None
    oValue = dSection.get("v_files", VERILOG) if isinstance(dSection, dict) else VERILOG
    sValue = str(oValue).lower() if oValue is not None else VERILOG
    if sValue not in VERILOG_LANGUAGES:
        raise exceptions.ConfigurationError(f"ERROR: v_files in the systemverilog section is {oValue}, not one of {', '.join(VERILOG_LANGUAGES)}")
    return sValue


def of_file(sFileName, dConfig=None):
    """Returns the language of a file from its name; .v and .vh files as v_files of the configuration says."""
    sExtension = os.path.splitext(sFileName)[1].lower() if sFileName else ""
    if sExtension in SYSTEMVERILOG_EXTENSIONS:
        return SYSTEMVERILOG
    if sExtension in VERILOG_EXTENSIONS:
        return v_files(dConfig)
    return VHDL


def is_verilog(sFileName):
    """True for a Verilog or SystemVerilog file, which svFile reads, whatever v_files says."""
    return bool(sFileName) and os.path.splitext(sFileName)[1].lower() in VERILOG_EXTENSIONS + SYSTEMVERILOG_EXTENSIONS


def file_class(sLanguageName):
    """Returns the class that reads files of a language: vhdlFile or svFile."""
    if sLanguageName in VERILOG_LANGUAGES:
        from mhsg.svFile import svFile  # pylint: disable=import-outside-toplevel

        return svFile
    from mhsg.vhdlFile import vhdlFile  # pylint: disable=import-outside-toplevel

    return vhdlFile
