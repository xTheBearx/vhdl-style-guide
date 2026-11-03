# -*- coding: utf-8 -*-
"""
The language of a file, from its extension: SystemVerilog for .sv, .svh, .v and .vh, VHDL for anything else.
Verilog files are read as SystemVerilog, of which Verilog is a subset.
"""

import os

VHDL = "vhdl"
SYSTEMVERILOG = "systemverilog"
LANGUAGES = (VHDL, SYSTEMVERILOG)

SYSTEMVERILOG_EXTENSIONS = (".sv", ".svh", ".v", ".vh")


def of_file(sFileName):
    """Returns the language of a file from its name."""
    if sFileName and os.path.splitext(sFileName)[1].lower() in SYSTEMVERILOG_EXTENSIONS:
        return SYSTEMVERILOG
    return VHDL


def file_class(sLanguageName):
    """Returns the class that reads files of a language: vhdlFile or svFile."""
    if sLanguageName == SYSTEMVERILOG:
        from mhsg.svFile import svFile  # pylint: disable=import-outside-toplevel

        return svFile
    from mhsg.vhdlFile import vhdlFile  # pylint: disable=import-outside-toplevel

    return vhdlFile
