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

import yaml

from mhsg import exceptions, vhdlFile
from mhsg.design import (
    analysis,
    black_box,
    cdc,
    flat,
    graph,
    netlist,
    project,
    runner,
    top,
)
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
        self.assertEqual(sorted(s for s in os.listdir(sTestDir) if s.endswith(".vhd")), [os.path.basename(s) for s in oDesign.all_files()])
        self.assertEqual({"WIDTH": 8}, oDesign.generics)

    def test_exclude_and_work_directory(self):
        oDesign = project.from_configuration(
            {
                "design": {
                    "top": "latch_top",
                    "work_directory": "build/design",
                    "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "*.vhd")], "exclude": ["*/un*.vhd", "*/depth.vhd"]}],
                },
            },
        )
        lFiles = [os.path.basename(s) for s in oDesign.all_files()]
        self.assertNotIn("undeclared.vhd", lFiles)
        self.assertNotIn("depth.vhd", lFiles)
        self.assertIn("latch.vhd", lFiles)
        self.assertEqual("build/design", oDesign.work_directory)

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


class test_cdc_configuration(unittest.TestCase):
    def design(self, dCdc):
        return project.from_configuration(
            {"design": {"top": "cdc_top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "cdc.vhd")]}], "cdc": dCdc}},
        )

    def test_valid(self):
        dCdc = {
            "clocks": {"sys": "clk_a"},
            "clock_groups": [["sys", "clk_b"]],
            "inputs": {"rst_a": "async"},
            "waivers": [{"signal": "x", "justification": "y"}],
        }
        self.assertEqual(dCdc, self.design(dCdc).cdc)
        self.assertEqual({}, self.design(None).cdc)

    def test_errors(self):
        for dCdc in ([], {"unknown": 1}, {"clocks": ["clk_a"]}, {"clock_groups": ["clk_a"]}, {"waivers": [{"justification": "y"}]}):
            with self.subTest(dCdc), self.assertRaises(exceptions.ConfigurationError):
                self.design(dCdc)


class FakeCell:
    """A black box cell of the flat netlist, for testing declarations."""

    def __init__(self, sType, dPorts, dParameters=None, tPath=("u_box",)):
        self.type = sType
        self.path = tPath[:-1]
        self.name = tPath[-1]
        self.cell = {"parameters": dParameters or {}}
        self.connections = {s: [1] for s in dPorts}

    def is_black_box(self):
        return True

    def __repr__(self):
        return ".".join(self.path + (self.name,))


class test_black_box_declarations(unittest.TestCase):
    def library(self, dTypes, dInstances=None):
        oLibrary = black_box.Library()
        oLibrary.add_types(dTypes, "test")
        oLibrary.add_instances(dInstances or {}, "test")
        return oLibrary

    def instance(self, oLibrary, oCell):
        return black_box.Instance(oCell, oLibrary.find(oCell.type, repr(oCell)))

    def test_archetypes(self):
        oLibrary = self.library(
            {
                "BUFGCE": {"archetype": "clock_buffer", "input": "I", "output": "O", "enable": "CE"},
                "IBUF": {"archetype": "buffer", "input": "I", "output": "O"},
                "MMCM": {"archetype": "clock_generator", "input": "CLKIN", "outputs": ["CLKOUT*"], "reset": "RST", "locked": "LOCKED"},
                "ip": {"archetype": "single_clock", "clock": "aclk", "ports": {"irq": "async"}},
                "sync": {"archetype": "synchronizer", "destination_clock": "dclk", "input": "d", "output": "q", "stages": "STAGES"},
                "fifo": {"archetype": "dual_clock_fifo", "sides": {"wclk": ["din", "wr_en"], "rclk": ["dout", "rd_en"]}},
            },
        )
        oBuffer = self.instance(oLibrary, FakeCell("BUFGCE", ["I", "O", "CE"]))
        self.assertEqual(
            ("clock", "clock_out", "same", "enable"),
            (oBuffer.role("I").kind, oBuffer.role("O").kind, oBuffer.role("O").relation, oBuffer.role("ce").kind),
        )
        self.assertEqual(["I"], self.instance(oLibrary, FakeCell("IBUF", ["I", "O"])).role("O").inputs)
        oMmcm = self.instance(oLibrary, FakeCell("MMCM", ["CLKIN", "CLKOUT0", "CLKOUT1", "RST", "LOCKED"]))
        self.assertEqual(
            ["clock", "clock_out", "clock_out", "reset_in", "async"],
            [oMmcm.role(s).kind for s in ("CLKIN", "CLKOUT0", "CLKOUT1", "RST", "LOCKED")],
        )
        self.assertEqual("derived", oMmcm.role("CLKOUT1").relation)
        oIp = self.instance(oLibrary, FakeCell("ip", ["aclk", "s_data", "irq"]))
        self.assertEqual(("clock", "sync", "aclk", "async"), (oIp.role("aclk").kind, oIp.role("s_data").kind, oIp.role("s_data").clock, oIp.role("irq").kind))
        oSync = self.instance(oLibrary, FakeCell("sync", ["dclk", "d", "q"], {"STAGES": "00000000000000000000000000000011"}))
        self.assertEqual(("async", "synchronized", 3), (oSync.role("d").kind, oSync.role("q").kind, oSync.stages(oSync.role("q"))))
        oFifo = self.instance(oLibrary, FakeCell("fifo", ["wclk", "rclk", "din", "dout", "wr_en", "rd_en"]))
        self.assertEqual(["wclk", "rclk"], [oFifo.role(s).clock for s in ("din", "dout")])
        self.assertEqual([], oFifo.problems({s: "input" for s in oFifo.cell.connections}))

    def test_problems(self):
        oLibrary = self.library(
            {
                "ip": {"ports": {"clk": "clock", "data": "TODO", "cfg": {"static": "Set at boot"}, "missing": "async"}},
                "reviewed": {"reviewed_by": "A. Reviewer", "ports": {"cfg": {"static": "Set at boot"}}},
            },
        )
        oIp = self.instance(oLibrary, FakeCell("ip", ["clk", "data", "cfg", "other"]))
        self.assertEqual(
            [
                "port data has no role",
                "port other has no role",
                "static port cfg needs reviewed_by",
                "the declaration names port missing, which ip does not have",
            ],
            oIp.problems({s: "input" for s in ("clk", "data", "cfg", "other")}),
        )
        oReviewed = self.instance(oLibrary, FakeCell("reviewed", ["cfg"]))
        self.assertEqual([], oReviewed.problems({"cfg": "input"}))
        self.assertFalse(self.instance(oLibrary, FakeCell("unknown", ["a"])).declared())

    def test_variants_and_instances(self):
        oLibrary = self.library(
            {
                "fifo_ip": {
                    "ports": {"clk": "clock", "rclk": "clock", "dout": {"sync": "rclk"}},
                    "variants": [{"when": {"COMMON_CLOCK": 1}, "ports": {"dout": {"sync": "clk"}}}],
                },
            },
            {"top.u_special": {"ports": {"dout": "async"}}},
        )
        oCommon = self.instance(oLibrary, FakeCell("fifo_ip", ["clk", "rclk", "dout"], {"COMMON_CLOCK": "1"}))
        oIndependent = self.instance(oLibrary, FakeCell("fifo_ip", ["clk", "rclk", "dout"], {"COMMON_CLOCK": "0"}))
        oSpecial = self.instance(oLibrary, FakeCell("fifo_ip", ["clk", "rclk", "dout"], {}, ("top", "u_special")))
        self.assertEqual(("clk", "rclk", "async"), (oCommon.role("dout").clock, oIndependent.role("dout").clock, oSpecial.role("dout").kind))
        self.assertEqual("clock", oSpecial.role("clk").kind)

    def test_errors(self):
        for dTypes in (
            {"x": {"ports": {"a": "fast"}}},
            {"x": {"ports": {"a": {"sync": "c", "path": ["b"]}}}},
            {"x": {"ports": {"a": {"clock_out": {"from": "c", "relation": "sideways"}}}}},
            {"x": {"archetype": "teleporter"}},
            {"x": {"archetype": "buffer", "input": "I"}},
            {"x": {"colour": "blue"}},
            {"x": {"variants": [{"ports": {}}]}},
        ):
            with self.subTest(dTypes), self.assertRaises(exceptions.ConfigurationError):
                self.library(dTypes)

    def test_library_files(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sLibrary = os.path.join(sDirectory, "vendor.yaml")
            with open(sLibrary, "w", encoding="utf-8") as oFile:
                json.dump(
                    {
                        "black_boxes": {
                            "BUFG": {"archetype": "clock_buffer", "input": "I", "output": "O"},
                            "IBUF": {"archetype": "buffer", "input": "I", "output": "O"},
                        },
                    },
                    oFile,
                )
            oLibrary = black_box.from_design({"black_box_libraries": [sLibrary], "black_boxes": {"IBUF": {"ports": {"I": "unused", "O": "async"}}}})
        # The design section takes precedence over the library
        self.assertEqual("async", self.instance(oLibrary, FakeCell("IBUF", ["I", "O"])).role("O").kind)
        self.assertEqual("clock_out", self.instance(oLibrary, FakeCell("BUFG", ["I", "O"])).role("O").kind)
        self.assertEqual([sLibrary], [o.source for o in oLibrary.find("BUFG", "u")])


class test_flat(unittest.TestCase):
    def test_instances_are_flattened(self):
        dChild = {
            "ports": {"a": {"direction": "input", "bits": [2]}, "y": {"direction": "output", "bits": [3]}},
            "cells": {"\\5": {"type": "$not", "port_directions": {"A": "input", "Y": "output"}, "connections": {"A": [2], "Y": [3]}}},
            "netnames": {},
        }
        dTop = {
            "ports": {"i": {"direction": "input", "bits": [2]}, "o": {"direction": "output", "bits": [4]}},
            "cells": {
                "u_1": {"type": "child", "connections": {"a": [2], "y": [3]}},
                "u_2": {"type": "child", "connections": {"a": [3], "y": [4]}},
            },
            "netnames": {"mid": {"bits": [3], "hide_name": 0}},
        }
        oFlat = flat.FlatDesign(netlist.Netlist({"modules": {"child": dChild, "top": dTop}}, {}))
        self.assertEqual("top", oFlat.top)
        self.assertEqual([("u_1",), ("u_2",)], sorted(o.path for o in oFlat.cells))
        oFirst, oSecond = sorted(oFlat.cells, key=lambda o: o.path)
        # The output of the first instance is the input of the second, through the net mid of the top
        self.assertEqual(oFirst.connections["Y"], oSecond.connections["A"])
        self.assertEqual("mid", oFlat.net_name(oFirst.connections["Y"][0]))
        self.assertEqual("i", oFlat.net_name(oFirst.connections["A"][0]))
        self.assertEqual(oFlat.top_ports["o"][1], oSecond.connections["Y"])


class test_top(unittest.TestCase):
    def design(self, dGenerics):
        return project.from_configuration(
            {"design": {"top": "real_top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "real_generic.vhd")]}], "generics": dGenerics}},
        )

    def test_missing_and_unknown_generics(self):
        oDesign = self.design({"WIDTH": 8, "SPEED": 1})
        self.assertEqual([("FREQ_HZ", 6)], [(sName, iLine) for sFile, iLine, sName in top.missing_generics(oDesign)])
        self.assertEqual(["SPEED"], [sName for sFile, iLine, sName in top.unknown_generics(oDesign)])
        self.assertEqual([], top.missing_generics(self.design({"FREQ_HZ": 1.0e6, "WIDTH": 8})))

    def test_patch_real_generics(self):
        oDesign = self.design({"FREQ_HZ": 100.0e6, "RATE_HZ": 2000, "WIDTH": 8})
        with tempfile.TemporaryDirectory() as sDirectory:
            sOriginal, sCopy, lPatched = top.patch_real_generics(oDesign, sDirectory)
            with open(sCopy, encoding="utf-8") as oFile:
                lCopy = oFile.read().splitlines()
        with open(sOriginal, encoding="utf-8") as oFile:
            lOriginal = oFile.read().splitlines()
        self.assertEqual(["FREQ_HZ", "RATE_HZ"], lPatched)
        # Every line stays in place, so findings in the copy have the lines of the original
        self.assertEqual(len(lOriginal), len(lCopy))
        self.assertEqual("    FREQ_HZ : real := 100000000.0;", lCopy[5])
        self.assertEqual("    RATE_HZ : real     := 2000.0;", lCopy[6])
        self.assertEqual(lOriginal[7:], lCopy[7:])
        self.assertIn("WIDTH=8", " ".join(runner.elaboration_options(oDesign, sDirectory, lPatched)))
        self.assertNotIn("FREQ_HZ", " ".join(runner.elaboration_options(oDesign, sDirectory, lPatched)))

    def test_real_literal(self):
        self.assertEqual("100000000.0", top.real_literal(1e8))
        self.assertEqual("1.0e+20", top.real_literal(1e20))
        self.assertEqual("2.5", top.real_literal("2.5"))

    def test_generic_declarations(self):
        lLines, _ = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "real_generic.vhd"))
        lDeclarations = top.generic_declarations(vhdlFile.vhdlFile(lLines), "real_top")
        self.assertEqual([["FREQ_HZ"], ["RATE_HZ"], ["WIDTH"]], [[s for s, i in d["names"]] for d in lDeclarations])
        self.assertEqual(["real", "real", "positive"], [d["type"] for d in lDeclarations])
        self.assertEqual([False, True, False], [d["default"] is not None for d in lDeclarations])


class test_graph(unittest.TestCase):
    def test_strongly_connected(self):
        dEdges = {1: [2], 2: [3], 3: [2], 4: [1], 5: [5]}
        lComponents = graph.strongly_connected([1, 2, 3, 4, 5], lambda i: dEdges.get(i, []))
        self.assertEqual([[2, 3], [1], [4], [5]], [sorted(l) for l in lComponents])

    def module(self, dCells, dPorts=None):
        dModule = {"ports": dPorts or {}, "cells": dCells, "netnames": {}}
        oDesign = graph.DesignGraph(netlist.Netlist({"modules": {"m": dModule}}, {}))
        return oDesign.graph("m")

    def test_bit_level_dependencies(self):
        oModule = self.module(
            {
                "add": {"type": "$add", "connections": {"A": [2, 3], "B": [4, 5], "Y": [6, 7]}},
                "mux": {"type": "$mux", "connections": {"A": [2, 3], "B": [4, 5], "S": [8], "Y": [9, 10]}},
                "ff": {"type": "$dff", "connections": {"CLK": [1], "D": [6, 7], "Q": [11, 12]}},
            },
        )
        # A carry moves to the more significant bits only
        self.assertEqual([2, 4], sorted(oModule.comb_drivers(6)))
        self.assertEqual([2, 3, 4, 5], sorted(oModule.comb_drivers(7)))
        self.assertEqual([3, 5, 8], sorted(oModule.comb_drivers(10)))
        # A register breaks the path
        self.assertEqual([], oModule.comb_drivers(11))

    def test_loops_and_latches(self):
        # A multiplexer feeding back to itself is a latch, not a loop; two cells feeding each other are a loop
        oModule = self.module(
            {
                "latch": {"type": "$mux", "connections": {"A": [2], "B": [3], "S": [4], "Y": [2]}},
                "a": {"type": "$and", "connections": {"A": [5], "B": [3], "Y": [6]}},
                "b": {"type": "$or", "connections": {"A": [6], "B": [4], "Y": [5]}},
            },
        )
        self.assertEqual([[5, 6]], [sorted(l) for l in oModule.loops()])

    def test_register_value(self):
        oModule = self.module(
            {
                "hold": {"type": "$mux", "connections": {"A": [3], "B": ["0"], "S": [4], "Y": [5]}},
                "stuck": {"type": "$adff", "parameters": {"ARST_VALUE": "0"}, "connections": {"CLK": [1], "ARST": [2], "D": [5], "Q": [3]}},
                "once": {"type": "$adff", "parameters": {"ARST_VALUE": "0"}, "connections": {"CLK": [1], "ARST": [2], "D": ["1"], "Q": [6]}},
                "data": {"type": "$dff", "connections": {"CLK": [1], "D": [4], "Q": [7]}},
            },
        )
        self.assertEqual("0", oModule.register_value("stuck", 0))
        self.assertIsNone(oModule.register_value("once", 0))
        self.assertIsNone(oModule.register_value("data", 0))

    def test_verilog_instance_name(self):
        self.assertEqual("data_ram_gen_n1_data_ram_inst", netlist.verilog_instance_name("data_ram_gen:1.data_ram_inst"))
        self.assertEqual("u_core", netlist.verilog_instance_name("u_core"))


@unittest.skipUnless(tools_installed(), "GHDL, Yosys and the GHDL plugin are not installed")
class test_design_analysis(unittest.TestCase):
    def run_design(self, sTop, sFile, lArguments=(), dGenerics=None, dRules=None, dCdc=None):
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            dDesign = {"top": sTop, "libraries": [{"name": "work", "files": [os.path.join(sTestDir, sFile)]}]}
            if dGenerics:
                dDesign["generics"] = dGenerics
            if dCdc:
                dDesign["cdc"] = dCdc
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign, "rule": dRules or {}}, oFile)
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

    def findings(self, sTop, sFile, **dOptions):
        """Returns the findings as (file name, line, rule, message)."""
        _, lOutput = self.run_design(sTop, sFile, **dOptions)
        lReturn = []
        for sLine in lOutput:
            sLocation, sMessage = sLine.split(": ", 1)[1].split(" -- ", 1)
            sFile, sRest = sLocation.rsplit("(", 1)
            sLineNumber, sRule = sRest.split(")", 1)
            # A finding without a location is reported under the name of the top entity, at line 0
            sFile = None if sFile == sTop else os.path.basename(sFile)
            lReturn.append((sFile, int(sLineNumber), sRule, sMessage))
        return lReturn

    def test_combinational_loops(self):
        self.assertEqual(
            [
                ("loop.vhd", 40, "design_003", "Combinational loop through a, b in loop_top"),
                ("loop.vhd", 45, "design_003", "Combinational loop through e, f in loop_top and instance u_pass"),
            ],
            self.findings("loop_top", "loop.vhd"),
        )

    def test_multiple_drivers(self):
        # The bidirectional pin is not reported
        self.assertEqual(
            [("multiple_drivers.vhd", 37, "design_004", "Signal shared_net in md_top has 2 drivers: u_first, u_second")],
            self.findings("md_top", "multiple_drivers.vhd"),
        )

    def test_registers(self):
        # ready_r changes once after reset and q_r has an enable: neither is reported
        self.assertEqual(
            [
                ("registers.vhd", 24, "design_006", "Signal missing in registers_top is read but never assigned"),
                ("registers.vhd", 33, "design_006", "Register count in registers_top is never used"),
                ("registers.vhd", 37, "design_005", "Register busy_r in registers_top never changes: it is always 0"),
            ],
            [t for t in self.findings("registers_top", "registers.vhd") if t[2] in ("design_005", "design_006")],
        )

    def test_logic_depth(self):
        # Two levels in the adder entity and one in the top: the path is reported once, where it ends
        self.assertEqual(
            [("depth.vhd", 53, "design_007", "Path of 3 logic levels to register q in depth_top, more than 2")],
            self.findings("depth_top", "depth.vhd", dRules={"design_007": {"maximum_depth": 2}}),
        )
        self.assertEqual([], self.findings("depth_top", "depth.vhd"))

    def test_generics(self):
        lFindings = self.findings("real_top", "real_generic.vhd", dGenerics={"WIDTH": 4})
        self.assertEqual(
            [("real_generic.vhd", 6, "design_001", "Design configuration error: generic FREQ_HZ of real_top has no default value; set it under generics")],
            lFindings,
        )
        # A real generic is set in a copy of the file, and findings still name the original
        self.assertEqual([], self.findings("real_top", "real_generic.vhd", dGenerics={"WIDTH": 4, "FREQ_HZ": 100.0e6}))

    def test_clock_domain_crossings(self):
        self.assertEqual(
            [
                ("cdc.vhd", 69, "design_010", "Clock clk_b is used as data"),
                ("cdc.vhd", 81, "design_013", "Clock div_a is made by a register from clk_a (1 register)"),
                ("cdc.vhd", 90, "design_008", "unsync_b (clk_b) captures flag_a (clk_a) without a synchronizer"),
                ("cdc.vhd", 93, "design_009", "Logic on x_a (clk_a), y_a (clk_a) before synchronizer logic1_b (clk_b) can glitch"),
                ("cdc.vhd", 95, "design_009", "bus_a (clk_a) is synchronized bit by bit into bus1_b (clk_b); the bits can arrive in different cycles"),
                ("cdc.vhd", 136, "design_015", "Reset rst_a is released asynchronously: it resets registers clocked by clk_a without a reset synchronizer"),
                ("cdc.vhd", 146, "design_015", "Reset rst_b is synchronized to clk_b, resets registers clocked by clk_a"),
                ("cdc.vhd", 163, "design_014", "Asynchronous reset is made by logic of rst_b, soft_a"),
                ("cdc.vhd", 170, "design_012", "Clock clk_a is gated by logic into clk_gated (1 register)"),
                ("cdc.vhd", 198, "design_011", "clk_c is used as a clock and as an asynchronous reset"),
                ("cdc.vhd", 198, "design_015", "Reset clk_c is released asynchronously: it resets registers clocked by clk_a without a reset synchronizer"),
            ],
            self.findings("cdc_top", "cdc.vhd"),
        )

    def test_cdc_rule_set(self):
        _, lOutput = self.run_design("cdc_top", "cdc.vhd", ["--lint", "--rule_set", "cdc"])
        self.assertIn(
            f"ERROR: {os.path.join(sTestDir, 'cdc.vhd')}(90)CDC-001 (design_008) -- unsync_b (clk_b) captures flag_a (clk_a) without a synchronizer",
            lOutput,
        )
        self.assertIn(
            f"WARNING: {os.path.join(sTestDir, 'cdc.vhd')}(170)CDC-005 (design_012) -- Clock clk_a is gated by logic into clk_gated (1 register)",
            lOutput,
        )

    def test_reconvergence(self):
        # Reported: two signals meeting directly, one signal through two synchronizers, a meeting after more registers,
        # and a flag set and cleared by two signals. Not reported: the gray-coded bus, the edge detector on one signal,
        # the register after a meeting, and the registers behind a synchronous reset, unless follow_resets is set.
        lExpected = [
            (
                "reconvergence.vhd",
                71,
                "design_016",
                "Separately synchronized mode_a (by mode_meta) and start_a (by start_meta) from clk_a meet again in go_b (clk_b)",
            ),
            (
                "reconvergence.vhd",
                82,
                "design_016",
                "Separately synchronized flag_a (by first1_b) and flag_a (by second1_b) from clk_a meet again in differ_b (clk_b)",
            ),
            (
                "reconvergence.vhd",
                88,
                "design_016",
                "Separately synchronized mode_a (by mode_meta) and start_a (by start_meta) from clk_a meet again in late_b (clk_b)",
            ),
            (
                "reconvergence.vhd",
                93,
                "design_016",
                "Separately synchronized mode_a (by mode_meta) and start_a (by start_meta) from clk_a meet again in busy_b (clk_b)",
            ),
        ]
        self.assertEqual(lExpected, self.findings("reconvergence_top", "reconvergence.vhd"))
        lResets = [
            (
                "reconvergence.vhd",
                101,
                "design_016",
                "Separately synchronized rst_a (by rst_meta) and start_a (by start_meta) from clk_a meet again in count1_b (clk_b)",
            ),
            (
                "reconvergence.vhd",
                102,
                "design_016",
                "Separately synchronized rst_a (by rst_meta) and start_a (by start_meta) from clk_a meet again in count2_b (clk_b)",
            ),
        ]
        self.assertEqual(lExpected + lResets, self.findings("reconvergence_top", "reconvergence.vhd", dRules={"design_016": {"follow_resets": True}}))
        with tempfile.TemporaryDirectory() as sDirectory:
            sJson = os.path.join(sDirectory, "cdc.json")
            self.run_design("reconvergence_top", "reconvergence.vhd", ["--cdc_report", sJson])
            with open(sJson, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
        self.assertEqual(
            {
                "synchronizers": [
                    {"signal": "mode_a", "synchronizer": "mode_meta", "clock": "clk_a"},
                    {"signal": "start_a", "synchronizer": "start_meta", "clock": "clk_a"},
                ],
                "clock": "clk_b",
                "points": ["go_b"],
            },
            {k: v for k, v in [d for d in dReport["reconvergences"] if d["points"] == ["go_b"]][0].items() if k != "location"},
        )
        self.assertEqual(["count1_b", "count2_b"], [d["points"][0] for d in dReport["reconvergences_through_resets"]])

    def test_black_boxes(self):
        # A component without an entity is a black box: the clock comes from its output, it is not undriven
        with tempfile.TemporaryDirectory() as sDirectory:
            sJson = os.path.join(sDirectory, "cdc.json")
            self.run_design("bb_top", "black_box.vhd", ["--cdc_report", sJson])
            with open(sJson, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
        self.assertEqual([("u_buf.O", "box", 1)], [(d["name"], d["kind"], d["registers"]) for d in dReport["clocks"]])

    def run_black_box_design(self, lArguments=()):
        with open(os.path.join(sTestDir, "black_box_cdc.yaml"), encoding="utf-8") as oFile:
            dDeclarations = yaml.safe_load(oFile)
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            dDesign = {"top": "bbc_top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "black_box_cdc.vhd")]}], **dDeclarations}
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign}, oFile)
            lArguments = [s.replace("DIRECTORY", sDirectory) for s in lArguments]
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            dFiles = {}
            for sName in os.listdir(sDirectory):
                with open(os.path.join(sDirectory, sName), encoding="utf-8") as oFile:
                    dFiles[sName] = oFile.read()
        lFindings = []
        for sLine in oResult.stdout.splitlines():
            sLocation, sMessage = sLine.split(": ", 1)[1].split(" -- ", 1)
            sFile, sRest = sLocation.rsplit("(", 1)
            sLineNumber, sRule = sRest.split(")", 1)
            lFindings.append((os.path.basename(sFile), int(sLineNumber), sRule, sMessage))
        return lFindings, dFiles

    def test_declared_black_boxes(self):
        lFindings, dFiles = self.run_black_box_design(["--cdc_report", "DIRECTORY/cdc.json", "--black_box_template", "DIRECTORY/template.yaml"])
        self.assertEqual(
            [
                ("black_box_cdc.vhd", 116, "design_008", "irq_q (clk_pad) captures u_ip.irq (async) without a synchronizer"),
                (
                    "black_box_cdc.vhd",
                    146,
                    "design_016",
                    "Separately synchronized u_sync_flag.src_in (by u_sync_flag.dest_out) and u_sync_mode.src_in (by u_sync_mode.dest_out) from clk_pad meet again in both_b (clk_b)",
                ),
                ("black_box_cdc.vhd", 162, "design_008", "reg1 (u_gen.clk_out1) captures flag_a (clk_pad) without a synchronizer"),
                ("black_box_cdc.vhd", 167, "design_008", "u_ip.a_data (clk_pad) captures bdata_b (clk_b) without a synchronizer"),
                ("black_box_cdc.vhd", 167, "design_017", "Black box dual_ip: static port cfg needs reviewed_by"),
                (
                    "black_box_cdc.vhd",
                    181,
                    "design_015",
                    "Reset locked is released asynchronously: it resets registers clocked by clk_pad without a reset synchronizer",
                ),
                ("black_box_cdc.vhd", 187, "design_017", "Black box mystery has no declaration of its clock domain behaviour"),
            ],
            lFindings,
        )
        dReport = json.loads(dFiles["cdc.json"])
        # The clock passes through the input buffer and the clock buffer; the derived output joins its group
        self.assertEqual(
            [("clk_b", "clk_b", None), ("clk_pad", "clk_pad", None), ("u_gen.clk_out0", "clk_pad", "clk_pad"), ("u_gen.clk_out1", "u_gen.clk_out1", None)],
            [(d["name"], d["group"], d["from"]) for d in dReport["clocks"]],
        )
        self.assertEqual(
            [("u_sync_flag", "dest_out", "clk_pad", "clk_b", 3), ("u_sync_mode", "dest_out", "clk_pad", "clk_b", 3)],
            [(d["instance"], d["output"], d["from"], d["clock"], d["stages"]) for d in dReport["box_synchronizers"]],
        )
        self.assertEqual([{"port": "u_ip.cfg", "justification": "Set once at power up", "reviewed_by": ""}], dReport["static_ports"])
        self.assertEqual(["mystery"], [d["type"] for d in dReport["black_boxes"] if not d["declared"]])
        self.assertIn(
            "  mystery:\n    # Instances: u_mystery\n    reference: TODO\n    reviewed_by: TODO\n    ports:\n      y: TODO  # output, 1 bit\n      x: TODO  # input, 1 bit\n",
            dFiles["template.yaml"],
        )
        self.assertNotIn("IBUF", dFiles["template.yaml"])

    def test_crossing_report(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sJson = os.path.join(sDirectory, "cdc.json")
            sText = os.path.join(sDirectory, "cdc.txt")
            self.run_design("cdc_top", "cdc.vhd", ["--cdc_report", sJson])
            self.run_design("cdc_top", "cdc.vhd", ["--cdc_report", sText])
            with open(sJson, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
            with open(sText, encoding="utf-8") as oFile:
                sReport = oFile.read()
        self.assertEqual(
            {
                "bus1_b": cdc.BUS,
                "data_b": cdc.QUALIFIED,
                "gray1_b": cdc.GRAY,
                "logic1_b": cdc.LOGIC,
                "req1_b": cdc.SYNCHRONIZED,
                "sync1_b": cdc.SYNCHRONIZED,
                "unsync_b": cdc.UNSYNCHRONIZED,
            },
            {d["destination"]: d["status"] for d in dReport["crossings"]},
        )
        self.assertEqual(
            [("clk_a", "port", None), ("clk_b", "port", None), ("clk_c", "port", None), ("clk_gated", "logic", "clk_a"), ("div_a", "register", "clk_a")],
            [(d["name"], d["kind"], d["from"]) for d in dReport["clocks"]],
        )
        self.assertIn("  sync1_b (clk_b) <- flag_a (clk_a)\n    synchronized: 2 stages\n", sReport)
        self.assertIn(
            "Summary: 1 bus synchronized bit by bit, 1 gray-coded bus, 1 logic before synchronizer, 1 qualified by enable, 2 synchronized, 1 unsynchronized",
            sReport,
        )

    def test_crossing_constraints(self):
        # Grouped clocks do not cross, and a reset input declared in a domain is synchronous to it
        lFindings = self.findings("cdc_top", "cdc.vhd", dCdc={"clock_groups": [["clk_a", "clk_b"]], "inputs": {"rst_a": "clk_a"}})
        lRules = sorted({t[2] for t in lFindings})
        self.assertEqual(["design_010", "design_011", "design_012", "design_013", "design_014", "design_015"], lRules)
        self.assertEqual(
            ["Reset clk_c is released asynchronously: it resets registers clocked by clk_a without a reset synchronizer"],
            [t[3] for t in lFindings if t[2] == "design_015"],
        )

    def test_waivers(self):
        lFindings = self.findings(
            "cdc_top",
            "cdc.vhd",
            dCdc={"clocks": {"fast": "clk_a"}, "waivers": [{"signal": "unsync_b", "justification": "Test"}, {"signal": "bus1_*"}]},
        )
        lCrossings = [t for t in lFindings if t[2] in ("design_008", "design_009")]
        self.assertEqual(
            [
                ("cdc.vhd", 93, "design_009", "Logic on x_a (fast), y_a (fast) before synchronizer logic1_b (clk_b) can glitch"),
                ("cdc.vhd", 95, "design_009", "bus_a (fast) is synchronized bit by bit into bus1_b (clk_b); the bits can arrive in different cycles"),
                (None, 0, "design_008", "Waiver for bus1_* has no justification"),
            ],
            lCrossings,
        )

    def test_missing_design_section(self):
        oResult = subprocess.run([*utils.mhsg_exec(), "--design", "-of", "syntastic"], cwd=sRoot, capture_output=True, text=True, check=False)
        self.assertEqual(1, oResult.returncode)
        self.assertIn("design section", oResult.stdout)
