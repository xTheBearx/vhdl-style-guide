# -*- coding: utf-8 -*-
"""
Finds GHDL and Yosys with the GHDL plugin.

The plugin is a module Yosys loads with -m ghdl, or is built into Yosys, as in the MSYS2 packages for Windows, which
have no module to load. find checks once which it is, and module_options gives the options to pass to Yosys.
"""

import os
import shutil
import subprocess

from mhsg import exceptions

INSTALL_HINT = (
    "Design analysis needs GHDL, Yosys and the GHDL plugin for Yosys, for example from the packages ghdl, yosys and "
    "yosys-plugin-ghdl, or from the YosysHQ OSS CAD Suite."
)


# (Yosys, GHDL_PREFIX) -> whether the ghdl command is built into Yosys
dBuiltIn = {}


class Tools:
    def __init__(self, sGhdl, sYosys, dEnvironment, sGhdlVersion, sYosysVersion, bBuiltIn=False, bSlang=False):
        self.ghdl = sGhdl
        self.yosys = sYosys
        self.environment = dEnvironment
        self.ghdl_version = sGhdlVersion
        self.yosys_version = sYosysVersion
        # Whether the ghdl command is built into Yosys, so no module is loaded
        self.built_in = bBuiltIn
        # Whether Yosys has the read_slang command of the yosys-slang plugin, for SystemVerilog
        self.slang = bSlang

    def module_options(self):
        """Returns the options that make the ghdl command available in Yosys: none if it is built in, else -m ghdl."""
        return [] if self.built_in else ["-m", "ghdl"]


def find(bGhdl=True):
    """
    Returns the Tools, or raises a DesignError when they are missing or the plugin does not load. A design without
    VHDL, bGhdl False, needs only Yosys.
    """
    sGhdl = shutil.which("ghdl")
    sYosys = shutil.which("yosys")
    if sYosys is None or (bGhdl and sGhdl is None):
        raise exceptions.DesignError("ERROR: " + (INSTALL_HINT if bGhdl else "Design analysis of Verilog and SystemVerilog needs Yosys."))
    if not bGhdl:
        return Tools(sGhdl, sYosys, dict(os.environ), "", first_line([sYosys, "-V"]), bSlang=has_slang(sYosys))
    dEnvironment = dict(os.environ)
    if "GHDL_PREFIX" not in dEnvironment:
        # The plugin does not always find the libraries of the installed GHDL backend, so tell it where they are
        sPrefix = library_prefix(sGhdl)
        if sPrefix:
            dEnvironment["GHDL_PREFIX"] = sPrefix
    bBuiltIn = built_in(sYosys, dEnvironment)
    if not bBuiltIn:
        oPlugin = subprocess.run([sYosys, "-m", "ghdl", "-q", "-p", "help ghdl"], capture_output=True, text=True, env=dEnvironment, check=False)
        if oPlugin.returncode != 0:
            raise exceptions.DesignError("ERROR: Yosys cannot load the GHDL plugin. " + INSTALL_HINT)
    return Tools(sGhdl, sYosys, dEnvironment, first_line([sGhdl, "--version"]), first_line([sYosys, "-V"]), bBuiltIn, has_slang(sYosys))


# Yosys -> the options that give it the read_slang command, or None
dSlang = {}


def has_slang(sYosys):
    """Whether Yosys has the read_slang command, built in or from the slang plugin, checked once for each Yosys."""
    return slang_options(sYosys) is not None


def slang_options(sYosys):
    """The options that give Yosys the read_slang command: none when it is built in, -m slang for the plugin."""
    if sYosys not in dSlang:
        dSlang[sYosys] = None
        for lOptions in ([], ["-m", "slang"]):
            oHelp = subprocess.run([sYosys, *lOptions, "-Q", "-T", "-p", "help read_slang"], capture_output=True, text=True, check=False)
            if oHelp.returncode == 0 and "No such command" not in oHelp.stdout + oHelp.stderr:
                dSlang[sYosys] = lOptions
                break
    return dSlang[sYosys]


def built_in(sYosys, dEnvironment):
    """
    Returns whether the ghdl command is built into Yosys, checked once for each Yosys and GHDL_PREFIX. Yosys exits
    with 0 from help for an unknown command too, so its output tells: "No such command" when it is not built in.
    """
    tKey = (sYosys, dEnvironment.get("GHDL_PREFIX"))
    if tKey not in dBuiltIn:
        oHelp = subprocess.run([sYosys, "-Q", "-T", "-p", "help ghdl"], capture_output=True, text=True, env=dEnvironment, check=False)
        sOutput = oHelp.stdout + oHelp.stderr
        dBuiltIn[tKey] = oHelp.returncode == 0 and "No such command" not in sOutput
    return dBuiltIn[tKey]


def library_prefix(sGhdl):
    oResult = subprocess.run([sGhdl, "--dispconfig"], capture_output=True, text=True, check=False)
    for sLine in oResult.stdout.splitlines():
        if sLine.startswith("library prefix:"):
            return sLine.split(":", 1)[1].strip()
    return None


def first_line(lCommand):
    oResult = subprocess.run(lCommand, capture_output=True, text=True, check=False)
    lLines = oResult.stdout.splitlines()
    return lLines[0].strip() if lLines else ""
