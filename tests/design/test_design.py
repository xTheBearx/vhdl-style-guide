# -*- coding: utf-8 -*-
"""
Tests for design analysis. The tests that run GHDL and Yosys are skipped when they are not installed.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

from mhsg import exceptions
from mhsg.design import analysis, netlist, project, runner
from tests import utils

sTestDir = os.path.dirname(os.path.abspath(__file__))
sRoot = os.path.dirname(os.path.dirname(sTestDir))


def tools_installed():
    """Returns whether GHDL, Yosys and the plugin can run. With MHSG_REQUIRE_DESIGN_TOOLS set, raises instead of returning False."""
    try:
        from mhsg.design import tools

        tools.find()
    except exceptions.DesignError:
        if os.environ.get("MHSG_REQUIRE_DESIGN_TOOLS"):
            raise
        return False
    return True


class test_project(unittest.TestCase):
    def test_design_section(self):
        oDesign = project.from_configuration(
            {"design": {"top": "latch_top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "*.vhd")]}], "generics": {"WIDTH": 8}}},
        )
        self.assertEqual("latch_top", oDesign.top)
        self.assertEqual("08", oDesign.standard)
        self.assertEqual("work", oDesign.top_library)
        self.assertEqual(["clean.vhd", "latch.vhd", "undeclared.vhd"], [os.path.basename(s) for s in oDesign.all_files()])
        self.assertEqual({"WIDTH": 8}, oDesign.generics)

    def test_files_from(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sList = os.path.join(sDirectory, "files.f")
            with open(sList, "w", encoding="utf-8") as oFile:
                oFile.write(f"# comment\n{os.path.join(sTestDir, 'latch.vhd')}\n\n// another\n{os.path.join(sTestDir, 'clean.vhd')}\n")
            oDesign = project.from_configuration({"design": {"top": "t", "libraries": [{"name": "lib", "files_from": sList}]}})
        self.assertEqual(["latch.vhd", "clean.vhd"], [os.path.basename(s) for s in oDesign.all_files()])

    def test_errors(self):
        for dConfiguration in (
            {},
            {"design": {"libraries": [{"name": "work", "files": [os.path.join(sTestDir, "latch.vhd")]}]}},
            {"design": {"top": "t", "libraries": [{"name": "work", "files": ["missing.vhd"]}]}},
            {"design": {"top": "t", "standard": "99", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "latch.vhd")]}]}},
        ):
            with self.subTest(dConfiguration), self.assertRaises(exceptions.ConfigurationError):
                project.from_configuration(dConfiguration)


class test_runner_messages(unittest.TestCase):
    def test_parse_messages(self):
        sOutput = "\n".join(
            [
                'src/a.vhd:14:3:error: no declaration for "x"',
                'src/a.vhd:20:1:warning: declaration of "y" hides signal',
                "src/top.vhd:405:5:(assert note): [NEORV32] configuration",
                "src/top.vhd:410:5:(assert failure): DEPTH must be positive",
                "/usr/bin/ghdl-mcode:error: compilation error",
            ],
        )
        lMessages = runner.parse_messages(sOutput, "analysis")
        self.assertEqual(
            [("src/a.vhd", 14, "error"), ("src/a.vhd", 20, "warning"), ("src/top.vhd", 405, "note"), ("src/top.vhd", 410, "error")],
            [(o.file, o.line, o.severity) for o in lMessages],
        )
        self.assertEqual("assertion failure: DEPTH must be positive", lMessages[3].text)


class test_netlist(unittest.TestCase):
    def setUp(self):
        self.sDirectory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.sDirectory)
        sVerilog = os.path.join(self.sDirectory, "design.v")
        with open(sVerilog, "w", encoding="utf-8") as oFile:
            oFile.write(
                "module latch_top\n  (input a);\n  wire n5_o;\n  reg n6_q;\n  /* latch.vhd:21:8  */\n  assign n5_o = ~a;\n"
                "  /* latch.vhd:14:3  */\n  always @(en)\n    n6_q <= a;\nendmodule\n",
            )
        self.dLocations = netlist.read_locations(sVerilog)
        dModule = {
            "ports": {"q": {"direction": "output", "bits": [3]}},
            "cells": {
                "\\5": {"type": "$not", "connections": {"A": [2], "Y": [4]}},
                "\\6": {"type": "$dlatch", "connections": {"D": [2], "EN": [5], "Q": [3]}},
                "\\7": {"type": "$mux", "connections": {"A": [6], "B": [7], "S": [5], "Y": [6]}},
            },
            "netnames": {"r": {"bits": [6], "hide_name": 0}},
        }
        self.oNetlist = netlist.Netlist({"modules": {"latch_top": dModule}}, self.dLocations)

    def test_locations(self):
        self.assertEqual("latch.vhd:14:3", repr(self.oNetlist.location("latch_top", "\\6")))
        self.assertEqual("latch.vhd:21:8", repr(self.oNetlist.location("latch_top", "\\5")))
        self.assertIsNone(self.oNetlist.location("latch_top", "\\7"))

    def test_latches(self):
        # A latch cell, and a multiplexer that feeds back to its own input
        self.assertEqual(["\\6", "\\7"], [sCell for sModule, sCell, dCell in self.oNetlist.latches()])
        self.assertEqual("q", self.oNetlist.bit_name("latch_top", 3))
        self.assertEqual("r", self.oNetlist.bit_name("latch_top", 6))

    def test_refine_to_assignment(self):
        oContext = analysis.Context(None, None, self.oNetlist)
        oLocation = netlist.Location(os.path.join(sTestDir, "latch.vhd"), 14, 3)
        self.assertEqual((oLocation.file, 17), oContext.refine(oLocation, "q"))
        self.assertEqual((oLocation.file, 14), oContext.refine(oLocation, "unknown"))
        self.assertEqual((None, 0), oContext.refine(None, "q"))


@unittest.skipUnless(tools_installed(), "GHDL, Yosys and the GHDL plugin are not installed")
class test_design_analysis(unittest.TestCase):
    def run_design(self, sTop, sFile, lArguments=()):
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": {"top": sTop, "libraries": [{"name": "work", "files": [os.path.join(sTestDir, sFile)]}]}}, oFile)
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        return oResult.returncode, oResult.stdout.splitlines()

    def test_latch(self):
        iStatus, lOutput = self.run_design("latch_top", "latch.vhd")
        self.assertEqual(1, iStatus)
        self.assertEqual([f"ERROR: {os.path.join(sTestDir, 'latch.vhd')}(17)design_002 -- Synthesis infers a latch for q in latch_top"], lOutput)

    def test_latch_with_rule_set(self):
        iStatus, lOutput = self.run_design("latch_top", "latch.vhd", ["--lint"])
        self.assertEqual(0, iStatus)
        self.assertEqual([f"WARNING: {os.path.join(sTestDir, 'latch.vhd')}(17)DO254-SS4 (design_002) -- Synthesis infers a latch for q in latch_top"], lOutput)

    def test_clean(self):
        self.assertEqual((0, []), self.run_design("clean_top", "clean.vhd"))

    def test_ghdl_error(self):
        iStatus, lOutput = self.run_design("undeclared_top", "undeclared.vhd")
        self.assertEqual(1, iStatus)
        self.assertEqual(1, len(lOutput))
        self.assertIn("undeclared.vhd(14)design_001 -- GHDL analysis error: no declaration for", lOutput[0])

    def test_missing_design_section(self):
        oResult = subprocess.run([*utils.mhsg_exec(), "--design", "-of", "syntastic"], cwd=sRoot, capture_output=True, text=True, check=False)
        self.assertEqual(1, oResult.returncode)
        self.assertIn("design section", oResult.stdout)
