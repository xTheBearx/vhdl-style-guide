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
from unittest import mock

import yaml

from mhsg import exceptions, version, vhdlFile
from mhsg.design import (
    analysis,
    black_box,
    cdc,
    flat,
    graph,
    netlist,
    project,
    runner,
    stubs,
    tools,
    top,
    vendors,
    verilog_black_boxes,
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


class test_verilog_designs(unittest.TestCase):
    def design(self, lFiles, dExtra=None):
        dDesign = {"top": "top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, s) for s in lFiles]}]}
        dDesign.update(dExtra or {})
        return project.from_configuration({"design": dDesign})

    def test_language(self):
        self.assertEqual("systemverilog", self.design(["cdc_sv.sv"]).language)
        self.assertEqual("mixed", self.design(["mixed_sync.v", "mixed_top.vhd"]).language)
        self.assertEqual("vhdl", self.design(["latch.vhd"]).language)

    def test_read_commands(self):
        oDesign = self.design(
            ["cdc_sv.sv"],
            {"defines": {"SIM": None, "WIDTH": 8}, "include_directories": ["inc"], "generics": {"Depth": 4, "Fast": True, "Name": "core"}},
        )
        oTools = tools.Tools(None, "yosys", {}, "", "")
        sScript, lOptions = runner.verilog_read(oDesign, oTools, "top")
        self.assertEqual([], lOptions)
        self.assertEqual(
            f"read_verilog -sv -DSIM -DWIDTH=8 -Iinc {os.path.join(sTestDir, 'cdc_sv.sv')}; hierarchy -check -top top -chparam Depth 4 -chparam Fast 1 -chparam Name \"core\"",
            sScript,
        )

    def test_messages(self):
        lMessages = runner.parse_verilog_messages(
            "/x/bad.v:2: ERROR: syntax error, unexpected ';'\nERROR: Module `\\sub' referenced in module `\\top' in cell `\\u_sub' is not part of the design.\n",
            "verilog",
        )
        self.assertEqual([("/x/bad.v", 2, "error"), (None, 0, "error")], [(o.file, o.line, o.severity) for o in lMessages])
        self.assertEqual("Module `sub' referenced in module `top' in cell `u_sub' is not part of the design.", lMessages[1].text)


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


# GHDL's Verilog output in later versions: src attributes on declarations and statements, and location comments with #
sSourceAttributes = """module sub_Brtl
  (input  clk_i,
   input  d_i,
   output q_o);
  (* src="sub.vhd:15.12" *) reg q_r;
  (* src="sub.vhd:21.9" *) reg n34;
  assign q_o = q_r; //(module output)
  /*# sub.vhd:21:9 */
  (* src="sub.vhd:21.9" *) always @(posedge clk_i)
    n34 <= d_i;
  (* src="sub.vhd:21.9" *) initial
    n34 = 1'b0;
endmodule

module top
  (input  clk_a,
   input  in_a,
   output [1:0] out_b);
  (* src="top.vhd:20.12" *) wire src_q;
  (* src="top.vhd:53.20" *) wire [1:0] n20;
  (* src="top.vhd:37.9" *) reg n22;
  assign out_b = n20; //(module output)
  /*# top.vhd:28:5 */
  (* src="top.vhd:28.5" *) sub_Brtl u_src (
    .clk_i(clk_a),
    .d_i(in_a),
    .q_o(src_q));
  /*# top.vhd:53:20 */
  assign n20 = {src_q, n22};
  /*# top.vhd:37:9 */
  (* src="top.vhd:37.9" *) always @(posedge clk_a)
    n22 <= in_a;
endmodule
"""


class test_netlist_locations(unittest.TestCase):
    """The locations of GHDL's Verilog in its different forms: comments, src attributes, or both."""

    def read(self, sText, lSourceFiles=None):
        with tempfile.TemporaryDirectory() as sDirectory:
            sVerilog = os.path.join(sDirectory, "design.v")
            with open(sVerilog, "w", encoding="utf-8") as oFile:
                oFile.write(sText)
            return {k: repr(v) for k, v in netlist.read_locations(sVerilog, lSourceFiles).items()}

    def test_comments_and_attributes(self):
        dExpected = {
            ("sub_Brtl", "34"): "sub.vhd:21:9",
            ("top", "20"): "top.vhd:53:20",
            ("top", "22"): "top.vhd:37:9",
            ("top", "instance u_src"): "top.vhd:28:5",
        }
        self.assertEqual(dExpected, self.read(sSourceAttributes))

    def test_attributes_only(self):
        # Without comments: the src attribute of the statement, else of the declaration of the output, as for n20
        sText = "\n".join(s for s in sSourceAttributes.splitlines() if "/*#" not in s) + "\n"
        dExpected = {
            ("sub_Brtl", "34"): "sub.vhd:21:9",
            ("top", "20"): "top.vhd:53:20",
            ("top", "22"): "top.vhd:37:9",
            ("top", "instance u_src"): "top.vhd:28:5",
        }
        self.assertEqual(dExpected, self.read(sText))

    def test_attribute_does_not_outlive_its_statement(self):
        # The assignment to n21 has no location of its own and must not take the one of the statement before it
        sText = (
            "module top\n  (input a);\n  wire n21;\n" '  (* src="top.vhd:30.3-32.5" *) always @(posedge a)\n    n7 <= a;\n' "  assign n21 = ~a;\nendmodule\n"
        )
        self.assertEqual({("top", "7"): "top.vhd:30:3"}, self.read(sText))

    def test_attribute_values(self):
        oLocation = netlist.source_location("/work/src/fifo.vhd:28.3-30.5")
        self.assertEqual(("/work/src/fifo.vhd", 28, 3), (oLocation.file, oLocation.line, oLocation.column))
        self.assertEqual("fifo.vhd:28:0", repr(netlist.source_location("fifo.vhd:28")))
        # Several locations: the first in a file of the design, else the first in a VHDL file
        sSource = "/lib/ieee/numeric_std-body.vhdl:120.5-121.9|src/fifo.vhd:42.5|src/top.vhd:7.1"
        self.assertEqual("/lib/ieee/numeric_std-body.vhdl:120:5", repr(netlist.source_location(sSource)))
        self.assertEqual("src/fifo.vhd:42:5", repr(netlist.source_location(sSource, netlist.source_file_set(["src/fifo.vhd", "src/top.vhd"]))))
        self.assertEqual("src/top.vhd:7:1", repr(netlist.source_location(sSource, netlist.source_file_set([os.path.abspath("src/top.vhd")]))))
        # Locations outside VHDL files, such as Yosys sources, are not locations of the design
        self.assertIsNone(netlist.source_location("ghdl.cc:832"))
        self.assertIsNone(netlist.source_location(None))
        self.assertEqual("top.vhd:3:1", repr(netlist.attribute_location('  (* keep, src = "top.vhd:3.1|ghdl.cc:9" *) reg n3;')))
        self.assertIsNone(netlist.attribute_location("  reg n3;"))

    def test_cell_names(self):
        # Yosys names the cells of the GHDL plugin \\34 or :34
        oNetlist = netlist.Netlist(
            {"modules": {"top": {"cells": {":34": {"type": "$dff"}, "\\35": {"type": "$dff"}}}}},
            {("top", "34"): "a", ("top", "35"): "b"},
        )
        self.assertEqual("a", oNetlist.location("top", ":34"))
        self.assertEqual("b", oNetlist.location("top", "\\35"))
        self.assertEqual("34", netlist.instance_number(":34"))
        self.assertEqual("data:1", netlist.instance_number("data:1"))

    def test_json_src_attribute(self):
        # A src attribute on a cell of the JSON netlist locates the cells the Verilog does not
        dModule = {
            "cells": {
                "\\5": {"type": "$not", "attributes": {"src": "ghdl.cc:12|latch.vhd:21.8-21.15"}},
                "\\6": {"type": "$dlatch", "attributes": {"src": "latch.vhd:14.3-19.26"}},
                "\\7": {"type": "$mux", "attributes": {}},
            },
        }
        oNetlist = netlist.Netlist({"modules": {"latch_top": dModule}}, {("latch_top", "6"): netlist.Location("latch.vhd", 14, 1)})
        self.assertEqual("latch.vhd:21:8", repr(oNetlist.location("latch_top", "\\5")))
        self.assertEqual("latch.vhd:14:1", repr(oNetlist.location("latch_top", "\\6")))
        self.assertIsNone(oNetlist.location("latch_top", "\\7"))

    def test_refine_from_declaration(self):
        # Later versions of GHDL locate the latch of q at the declaration of the port, line 7: refine finds the assignment
        oContext = analysis.Context(None, None, None)
        sFile = os.path.join(sTestDir, "latch.vhd")
        self.assertEqual((sFile, 17), oContext.refine(netlist.Location(sFile, 7, 5), "q"))
        # A concurrent assignment stays where it is
        self.assertEqual((sFile, 21), oContext.refine(netlist.Location(sFile, 21, 8), "r"))
        self.assertEqual((sFile, 7), oContext.refine(netlist.Location(sFile, 7, 5), "unknown"))


class test_tools(unittest.TestCase):
    """Yosys loads the GHDL plugin with -m ghdl, unless the ghdl command is built into it, as in MSYS2 on Windows."""

    def setUp(self):
        tools.dBuiltIn.clear()
        self.addCleanup(tools.dBuiltIn.clear)
        self.lCalls = []

    def fake_run(self, bBuiltIn):
        def run(lCommand, **dOptions):
            self.lCalls.append((lCommand, dOptions.get("env")))
            sStdout, iStatus = "", 0
            if lCommand[0] == "yosys" and "help ghdl" in lCommand:
                if "-m" in lCommand:
                    iStatus = 1 if bBuiltIn else 0
                elif not bBuiltIn:
                    sStdout = "-- Running command `help ghdl' --\nNo such command or cell type: ghdl\n"
                else:
                    sStdout = "-- Running command `help ghdl' --\n\n    ghdl [options] unit [arch]\n"
            elif lCommand[1:] == ["--dispconfig"]:
                sStdout = "library prefix: /usr/lib/ghdl\n"
            return subprocess.CompletedProcess(lCommand, iStatus, sStdout, "")

        return run

    def find(self, bBuiltIn, dEnvironment=None):
        with mock.patch.object(tools.shutil, "which", side_effect=lambda s: s), mock.patch.object(tools.subprocess, "run", side_effect=self.fake_run(bBuiltIn)):
            with mock.patch.dict(os.environ, dEnvironment or {}, clear=False):
                if not dEnvironment:
                    os.environ.pop("GHDL_PREFIX", None)
                return tools.find()

    def yosys_command(self, oTools):
        oDesign = project.from_configuration({"design": {"top": "clean_top", "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "clean.vhd")]}]}})
        with tempfile.TemporaryDirectory() as sDirectory, mock.patch.object(runner.subprocess, "run", side_effect=self.fake_run(oTools.built_in)):
            oResult = runner.run(oDesign, oTools, sDirectory)
        self.assertEqual("yosys", oResult.failed_stage)
        return oResult.commands[-1]

    def test_plugin_module(self):
        oTools = self.find(False)
        self.assertFalse(oTools.built_in)
        self.assertEqual(["-m", "ghdl"], oTools.module_options())
        self.assertEqual("/usr/lib/ghdl", oTools.environment["GHDL_PREFIX"])
        self.assertEqual(["yosys", "-m", "ghdl", "-q", "-l"], self.yosys_command(oTools)[:5])

    def test_built_in(self):
        oTools = self.find(True, {"GHDL_PREFIX": "C:/msys64/ucrt64/lib/ghdl"})
        self.assertTrue(oTools.built_in)
        self.assertEqual([], oTools.module_options())
        # GHDL_PREFIX from the environment is kept, and GHDL is not asked for its own
        self.assertEqual("C:/msys64/ucrt64/lib/ghdl", oTools.environment["GHDL_PREFIX"])
        self.assertFalse([l for l, _ in self.lCalls if l[1:] == ["--dispconfig"]])
        self.assertTrue(all(d["GHDL_PREFIX"] == "C:/msys64/ucrt64/lib/ghdl" for l, d in self.lCalls if "help ghdl" in l))
        # No -m ghdl, which fails without a module to load
        self.assertEqual(["yosys", "-q", "-l"], self.yosys_command(oTools)[:3])
        self.assertFalse([l for l, _ in self.lCalls if l[0] == "yosys" and "-m" in l])

    def test_answer_is_cached(self):
        self.find(True, {"GHDL_PREFIX": "/opt/ghdl"})
        self.find(True, {"GHDL_PREFIX": "/opt/ghdl"})
        self.assertEqual(1, len([l for l, _ in self.lCalls if l[0] == "yosys" and "help ghdl" in l]))

    def test_no_plugin(self):
        def run(lCommand, **dOptions):
            if lCommand[0] == "yosys" and "help ghdl" in lCommand:
                return subprocess.CompletedProcess(lCommand, 1 if "-m" in lCommand else 0, "No such command or cell type: ghdl\n", "")
            return subprocess.CompletedProcess(lCommand, 0, "", "")

        with mock.patch.object(tools.shutil, "which", side_effect=lambda s: s), mock.patch.object(tools.subprocess, "run", side_effect=run):
            with self.assertRaises(exceptions.DesignError):
                tools.find()


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


class test_declaration_libraries(unittest.TestCase):
    def test_libraries_parse(self):
        self.assertEqual(["intel", "lattice", "microchip", "xilinx"], black_box.built_in_libraries())
        for sName in black_box.built_in_libraries():
            with self.subTest(sName):
                oLibrary = black_box.from_design({"black_box_libraries": [sName]})
                self.assertTrue(oLibrary.types)
                self.assertTrue(all(o.reference for o in oLibrary.types))
                # No library declaration needs a reviewer, which only the user can give
                self.assertFalse([o.name for o in oLibrary.types for _, r in o.ports if r is not None and r.kind == "static"])

    def test_documentation_is_up_to_date(self):
        """docs/black_box_library_<name>.rst is written with black_box.library_documentation(name)."""
        for sName in black_box.built_in_libraries():
            with self.subTest(sName), open(os.path.join(sRoot, "docs", f"black_box_library_{sName}.rst"), encoding="utf-8") as oFile:
                self.assertEqual(black_box.library_documentation(sName), oFile.read())

    def test_design_section_changes_single_ports(self):
        oLibrary = black_box.from_design(
            {"black_box_libraries": ["xilinx"], "black_boxes": {"BUFGMUX": {"ports": {"O": {"clock_out": {"from": "I0", "relation": "same"}}}}}},
        )
        oInstance = black_box.Instance(FakeCell("BUFGMUX", ["O", "I0", "I1", "S"]), oLibrary.find("BUFGMUX", "u_mux"))
        self.assertEqual(
            ("same", "I0", "async", "clock"),
            (oInstance.role("O").relation, oInstance.role("O").source, oInstance.role("S").kind, oInstance.role("I1").kind),
        )
        self.assertEqual(["design section", "library xilinx"], [o.source for o in oInstance.declarations])

    def test_unknown_library(self):
        with self.assertRaises(exceptions.ConfigurationError) as oContext:
            black_box.from_design({"black_box_libraries": ["acme"]})
        self.assertIn("not a file or a library that comes with mhsg (intel, lattice, microchip, xilinx)", oContext.exception.message)


class test_vendor_libraries(unittest.TestCase):
    def install(self, sDirectory, lFiles):
        for sFile in lFiles:
            sPath = os.path.join(sDirectory, sFile)
            os.makedirs(os.path.dirname(sPath), exist_ok=True)
            with open(sPath, "w", encoding="utf-8") as oFile:
                oFile.write("-- test\n")

    def libraries(self, lEntries, dEnvironment):
        return [(o.name, [os.path.basename(s) for s in o.files]) for o in vendors.resolve(lEntries, dEnvironment)]

    def test_vendors(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            self.install(
                sDirectory,
                [
                    "vivado/data/vhdl/src/unisims/unisim_VPKG.vhd",
                    "vivado/data/vhdl/src/unisims/unisim_VCOMP.vhd",
                    "vivado/data/ip/xpm/xpm_VCOMP.vhd",
                    "libero/Designer/lib/vhdl/polarfire.vhd",
                    "quartus/eda/sim_lib/altera_mf_components.vhd",
                    "quartus/eda/sim_lib/cyclonev_components.vhd",
                    "diamond/cae_library/synthesis/vhdl/ecp5u.vhd",
                ],
            )
            self.assertEqual(
                [("unisim", ["unisim_VPKG.vhd", "unisim_VCOMP.vhd"]), ("xpm", ["xpm_VCOMP.vhd"])],
                self.libraries(["xilinx"], {"XILINX_VIVADO": os.path.join(sDirectory, "vivado")}),
            )
            self.assertEqual(
                [("polarfire", ["polarfire.vhd"])],
                self.libraries([{"vendor": "microchip", "family": "PolarFire", "path": os.path.join(sDirectory, "libero")}], {}),
            )
            self.assertEqual(
                [("altera_mf", ["altera_mf_components.vhd"]), ("cyclonev", ["cyclonev_components.vhd"])],
                self.libraries([{"vendor": "intel", "family": "cyclonev"}], {"QUARTUS_ROOTDIR": os.path.join(sDirectory, "quartus")}),
            )
            self.assertEqual(
                [("ecp5u", ["ecp5u.vhd"])],
                self.libraries([{"vendor": "lattice", "family": "ecp5u"}], {"LSC_DIAMOND": os.path.join(sDirectory, "diamond")}),
            )
            # Explicit files, joined with the library of the same name
            sExtra = os.path.join(sDirectory, "my_unisim.vhd")
            self.install(sDirectory, ["my_unisim.vhd"])
            self.assertEqual(
                [("unisim", ["unisim_VPKG.vhd", "unisim_VCOMP.vhd", "my_unisim.vhd"]), ("xpm", ["xpm_VCOMP.vhd"])],
                self.libraries(["xilinx", {"library": "unisim", "files": [sExtra]}], {"XILINX_VIVADO": os.path.join(sDirectory, "vivado")}),
            )

    def test_errors(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            for lEntries, dEnvironment, sMessage in (
                (["xilinx"], {}, "the installation is not known"),
                (["xilinx"], {"XILINX_VIVADO": sDirectory}, "no declarations for library unisim were found. Tried:"),
                (["acme"], {}, "unknown vendor acme"),
                ([{"vendor": "microchip", "path": sDirectory}], {}, "needs family"),
                ([{"library": "unisim", "files": [os.path.join(sDirectory, "missing.vhd")]}], {}, "does not exist"),
                ([{"library": "unisim"}], {}, "lists no files"),
            ):
                with self.subTest(lEntries):
                    with self.assertRaises(exceptions.ConfigurationError) as oContext:
                        vendors.resolve(lEntries, dEnvironment)
                    self.assertIn(sMessage, oContext.exception.message)

    def test_vendor_libraries_come_first(self):
        oDesign = project.from_configuration(
            {
                "design": {
                    "top": "vendor_top",
                    "vendor_libraries": [{"vendor": "xilinx", "path": os.path.join(sTestDir, "vendor", "vivado")}],
                    "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "vendor_top.vhd")]}],
                },
            },
        )
        self.assertEqual(["unisim", "xpm", "work"], [o.name for o in oDesign.libraries])
        self.assertEqual("work", oDesign.top_library)


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

    def test_generic_values(self):
        self.assertEqual("10 ns", top.time_literal("10ns"))
        self.assertEqual("2.5 us", top.time_literal(" 2.5 us "))
        self.assertEqual("7 ns", top.time_literal(7))
        self.assertEqual("'1'", runner.value_text(1, "std_logic"))
        self.assertEqual("'b'", runner.value_text("b", "character"))
        self.assertEqual("1010", runner.value_text("1010", "std_logic_vector"))
        self.assertEqual("true", runner.value_text(True, "boolean"))

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
    def run_design(self, sTop, sFile, lArguments=(), dGenerics=None, dRules=None, dCdc=None, dDesignKeys=None, lWaivers=None):
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            lFiles = [sFile] if isinstance(sFile, str) else sFile
            dDesign = {"top": sTop, "libraries": [{"name": "work", "files": [os.path.join(sTestDir, s) for s in lFiles]}]}
            if dGenerics:
                dDesign["generics"] = dGenerics
            if dCdc:
                dDesign["cdc"] = dCdc
            dDesign.update(dDesignKeys or {})
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign, "rule": dRules or {}, **({"waivers": lWaivers} if lWaivers else {})}, oFile)
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        return oResult.returncode, oResult.stdout.splitlines()

    def test_systemverilog_cdc(self):
        # Yosys reads the SystemVerilog; findings are at the assignment, refined from the always block Yosys points at
        iStatus, lOutput = self.run_design("cdc_sv", "cdc_sv.sv", dCdc={"clocks": {"clk_a": "a", "clk_b": "b"}})
        sFile = os.path.join(sTestDir, "cdc_sv.sv")
        self.assertEqual(1, iStatus)
        self.assertEqual(
            [
                f"ERROR: {sFile}(16)design_010 -- Clock en_a is used as data",
                f"ERROR: {sFile}(18)design_015 -- Reset rst_ni is released asynchronously: it resets registers clocked by clk_a without a reset synchronizer (3 registers)",
                f"ERROR: {sFile}(30)design_008 -- unsync_b (clk_b) captures flag_a (clk_a) without a synchronizer",
                f"ERROR: {sFile}(43)design_009 -- Logic on x_a (clk_a), y_a (clk_a) before synchronizer s1x_b (clk_b) can glitch",
                f"ERROR: {sFile}(50)design_012 -- Clock clk_a is gated by logic into clk_gated (1 register)",
            ],
            lOutput,
        )

    def test_mixed_languages(self):
        # The VHDL top uses a Verilog synchronizer: Yosys links the instance GHDL leaves unbound to the module
        iStatus, lOutput = self.run_design("mixed_top", ["mixed_sync.v", "mixed_top.vhd"], dCdc={"clocks": {"clk_a": "a", "clk_b": "b"}})
        sFile = os.path.join(sTestDir, "mixed_top.vhd")
        self.assertEqual(1, iStatus)
        self.assertEqual(
            [
                f"ERROR: {sFile}(48)design_008 -- raw (clk_b) captures flag_a (clk_a) without a synchronizer",
                f"ERROR: {sFile}(49)design_008 -- raw_b (clk_b) captures flag_a (clk_a) without a synchronizer",
            ],
            lOutput,
        )

    def test_verilog_errors(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFile = os.path.join(sDirectory, "bad.v")
            with open(sFile, "w", encoding="utf-8") as oFile:
                oFile.write("module bad (input clk, output reg q);\n  always @(posedge clk) q <= ;\nendmodule\n")
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": {"top": "bad", "libraries": [{"name": "work", "files": [sFile]}]}}, oFile)
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic"],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual([f"ERROR: {sFile}(2)design_001 -- Yosys error: syntax error, unexpected ';'"], oResult.stdout.splitlines())

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

    def test_verilog_top(self):
        # The Verilog top uses a VHDL synchronizer: Yosys elaborates the entity with the ghdl command before reading
        # the Verilog. The crossing through it is synchronized; the one in the Verilog is not
        sFile = os.path.join(sTestDir, "vtop.v")
        for sOrder in ("listed", "auto"):
            iStatus, lOutput = self.run_design(
                "vtop",
                ["vtop_sync.vhd", "vtop.v"],
                dCdc={"clocks": {"clk_a": "a", "clk_b": "b"}},
                dDesignKeys={"order": sOrder},
            )
            self.assertEqual((1, [f"ERROR: {sFile}(21)design_008 -- raw (clk_b) captures flag_a (clk_a) without a synchronizer"]), (iStatus, lOutput), sOrder)

    def test_verilog_top_generics(self):
        # Each set of generic values is elaborated on its own, with the values pyslang computes: expressions and
        # parameters of the module holding the instance too. An instance in a generate loop that sets other values in
        # each iteration is analyzed with the defaults, which design_001 reports
        with tempfile.TemporaryDirectory() as sDirectory:
            iStatus, lOutput = self.run_design(
                "vtop_generics",
                ["vtop_generics.vhd", "vtop_generics.v"],
                dDesignKeys={"work_directory": sDirectory},
            )
            with open(os.path.join(sDirectory, "design.json"), encoding="utf-8") as oFile:
                dModules = json.load(oFile)["modules"]
        sFile = os.path.join(sTestDir, "vtop_generics.v")
        self.assertEqual(
            (
                1,
                [
                    f"ERROR: {sFile}(31)design_001 -- Design configuration error: Instance u_loop of vtop_reg is analyzed with the "
                    "defaults of its generics, as its own values cannot be set: the elaborations of module vtop_generics give it "
                    "different values",
                ],
            ),
            (iStatus, [s for s in lOutput if "design_001" in s]),
        )
        dTypes = {c: d["type"] for c, d in dModules["vtop_generics"]["cells"].items() if not d["type"].startswith("$")}
        dWidths = {c: len(dModules[t]["ports"]["d"]["bits"]) for c, t in dTypes.items()}
        self.assertEqual(
            {"u_named": 8, "u_position": 16, "g_reg.u_generate": 4, "u_expression": 8, "g_loop[1].u_loop": 4, "g_loop[2].u_loop": 4},
            dWidths,
        )
        # The instances with values of their own each have a module, elaborated from the entity with those values
        self.assertEqual("vtop_reg", dTypes["g_loop[1].u_loop"])
        self.assertEqual(4, len({dTypes[s] for s in ("u_named", "u_position", "g_reg.u_generate", "u_expression")}))
        self.assertTrue(all(dTypes[s].startswith("vtop_reg__mhsg") for s in ("u_named", "u_position", "g_reg.u_generate", "u_expression")))
        # The instance in the module with a parameter gets the width that parameter gives it
        sInner = dModules[dModules["vtop_generics"]["cells"]["u_mid"]["type"]]["cells"]["u_inner"]["type"]
        self.assertTrue(sInner.startswith("vtop_reg__mhsg"))
        self.assertEqual(6, len(dModules[sInner]["ports"]["d"]["bits"]))

    def test_combinational_loops(self):
        self.assertEqual(
            [
                ("loop.vhd", 40, "design_003", "Combinational loop through a, b in loop_top"),
                ("loop.vhd", 45, "design_003", "Combinational loop through e, f in loop_top and instance u_pass"),
            ],
            self.findings("loop_top", "loop.vhd"),
        )

    def test_reset_domain_crossings(self):
        # Only the register on the other reset is reported: the same reset, a reset that combines both and no reset
        # are safe
        self.assertEqual(
            [
                (
                    "rdc.vhd",
                    69,
                    "design_018",
                    "other_r, reset by rst_b, captures a_r, reset by rst_a: asserting rst_a alone can make it metastable",
                ),
            ],
            [t for t in self.findings("rdc_top", "rdc.vhd") if t[2] == "design_018"],
        )

    def test_clears(self):
        # A clear listed under clears is followed like data: x_a meets y_a in the registers it clears. Without the
        # list it is taken for a reset, as the synchronized reset of r3_b and r4_b is
        dCdc = {"clocks": {"clk_a": "a", "clk_b": "b"}}
        self.assertEqual([], self.findings("clear_top", "clear.vhd", dCdc=dCdc))
        sMessage = "Separately synchronized x_a (by x_meta) and y_a (by y_meta) from clk_a meet again in"
        self.assertEqual(
            [
                ("clear.vhd", 56, "design_016", f"{sMessage} r1_b (clk_b)"),
                ("clear.vhd", 57, "design_016", f"{sMessage} r2_b (clk_b)"),
            ],
            self.findings("clear_top", "clear.vhd", dCdc={**dCdc, "clears": ["clr_*"]}),
        )

    def test_reconvergence_in_black_boxes(self):
        # u_same samples both synchronized signals on its clock pin: they meet inside it. u_apart samples them on two
        # pins, so nothing is known about their meeting
        dDeclared = {
            "black_boxes": {"SAMPLER": {"ports": {"CLK": "clock", "CLK2": "clock", "A": {"sync": "CLK"}, "B": {"sync": "CLK"}, "Y": {"sync": "CLK"}}}},
            "black_box_instances": {"u_apart": {"ports": {"B": {"sync": "CLK2"}}}},
        }
        lFindings = self.findings("box_reconvergence_top", "box_reconvergence.vhd", dDesignKeys=dDeclared, dCdc={"clocks": {"clk_a": "a", "clk_b": "b"}})
        self.assertEqual(
            [
                (
                    "box_reconvergence.vhd",
                    55,
                    "design_016",
                    "Separately synchronized mode_a (by mode_meta) and start_a (by start_meta) from clk_a meet again in u_same",
                ),
            ],
            lFindings,
        )

    def test_paths_through_black_boxes(self):
        # A black box registers its outputs unless a declared path leads through it: then the loop through it and the
        # path through it count
        dDeclared = {"black_boxes": {"LUT_BUF": {"ports": {"O": {"path": ["I"]}}}}}
        dRules = {"design_007": {"maximum_depth": 2}}
        lFindings = self.findings("box_path_top", "box_path.vhd", dRules=dRules, dDesignKeys=dDeclared)
        self.assertEqual(
            [
                ("box_path.vhd", 34, "design_003", "Combinational loop through e, f in box_path_top and instance u_loop"),
                ("box_path.vhd", 56, "design_007", "Path of 3 logic levels to register r in box_path_top, more than 2"),
            ],
            [t for t in lFindings if t[2] in ("design_003", "design_007")],
        )
        lFindings = self.findings("box_path_top", "box_path.vhd", dRules=dRules)
        self.assertEqual([], [t for t in lFindings if t[2] in ("design_003", "design_007")])
        # A declaration of the single instance u_loop applies to it only: the loop through it is found, the path through
        # u_path is not
        dDeclared = {"black_box_instances": {"u_loop": {"ports": {"O": {"path": ["I"]}}}}}
        lFindings = self.findings("box_path_top", "box_path.vhd", dRules=dRules, dDesignKeys=dDeclared)
        self.assertEqual(
            [("box_path.vhd", 34, "design_003", "Combinational loop through e, f in box_path_top and instance u_loop")],
            [t for t in lFindings if t[2] in ("design_003", "design_007")],
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

    def test_generics_of_every_type(self):
        # time and real are patched into a copy of the top file; std_logic and character values are quoted for GHDL
        dGenerics = {"T_g": "5 ns", "E_g": 1, "C_g": "b", "R_g": 2.5, "V_g": "1010", "N_g": 3, "B_g": True, "S_g": "xy"}
        iStatus, lOutput = self.run_design("generic_types_top", "generic_types.vhd", dGenerics=dGenerics)
        self.assertEqual((0, []), (iStatus, lOutput))

    def test_verilog_black_boxes(self):
        # BUFGCE comes from Yosys' Xilinx cell models and vendor_ip from a stub; the crossings through them are found.
        # data_i, whose sync role does not say its direction, is an input, as its net has another driver
        dDeclaration = {"reviewed_by": "A. Reviewer", "ports": {"aclk": "clock", "data_i": {"sync": "aclk"}, "irq": "async"}}
        dKeys = {"black_box_libraries": ["xilinx"], "black_boxes": {"vendor_ip": dDeclaration}}
        self.assertEqual(
            [
                ("verilog_black_box.sv", 17, "design_008", "q_r (clk_b) captures d_r (clk_a) without a synchronizer"),
                ("verilog_black_box.sv", 21, "design_008", "irq_q (clk_a) captures u_ip.irq (async) without a synchronizer"),
            ],
            self.findings("vbb_top", "verilog_black_box.sv", dDesignKeys=dKeys),
        )
        # Without a declaration, the black box is reported, not the instance of a module that does not exist
        self.assertEqual(
            [("verilog_black_box.sv", 20, "design_017", "Black box vendor_ip has no declaration of its clock domain behaviour")],
            [
                t
                for t in self.findings("vbb_top", "verilog_black_box.sv", dDesignKeys={"black_box_libraries": ["xilinx"]})
                if t[2] in ("design_001", "design_017")
            ],
        )

    def test_waivers_of_findings(self):
        # A waived finding is left out of the findings and listed in the JSON output with its justification
        lWaivers = [
            {"rule": "design_005", "file": "registers.vhd", "line": 37, "justification": "busy_r is a placeholder for the next revision"},
            {"rule": "design_007", "justification": "Matches nothing here"},
        ]
        with tempfile.TemporaryDirectory() as sDirectory:
            sJson = os.path.join(sDirectory, "findings.json")
            _, lOutput = self.run_design("registers_top", "registers.vhd", ["--json", sJson], lWaivers=lWaivers)
            with open(sJson, encoding="utf-8") as oFile:
                dFindings = json.load(oFile)
        self.assertFalse(any("design_005" in s for s in lOutput))
        dFile = next(d for d in dFindings["files"] if d["file_path"].endswith("registers.vhd"))
        self.assertEqual(
            [
                {
                    "rule": "design_005",
                    "linenumber": 37,
                    "severity": "Error",
                    "solution": "Register busy_r in registers_top never changes: it is always 0",
                    "waiver": 1,
                    "justification": "busy_r is a placeholder for the next revision",
                },
            ],
            dFile["waived"],
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

    def test_vendor_declarations(self):
        # The design uses unisim and xpm, analyzed from the declaration files of a (stand-in) installation
        dDesign = {
            "top": "vendor_top",
            "vendor_libraries": ["xilinx"],
            "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "vendor_top.vhd")]}],
            "black_boxes": {
                "IBUF": {"archetype": "buffer", "input": "I", "output": "O"},
                "BUFG": {"archetype": "clock_buffer", "input": "I", "output": "O"},
                "xpm_cdc_single": {
                    "archetype": "synchronizer",
                    "source_clock": "src_clk",
                    "destination_clock": "dest_clk",
                    "input": "src_in",
                    "output": "dest_out",
                    "stages": "DEST_SYNC_FF",
                },
            },
        }
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            sReport = os.path.join(sDirectory, "cdc.json")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign}, oFile)
            dEnvironment = dict(os.environ, XILINX_VIVADO=os.path.join(sTestDir, "vendor", "vivado"))
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", "--cdc_report", sReport],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
                env=dEnvironment,
            )
            with open(sReport, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
        self.assertEqual((0, ""), (oResult.returncode, oResult.stdout))
        self.assertEqual([("clk_pad", "port", 1)], [(d["name"], d["kind"], d["registers"]) for d in dReport["clocks"]])
        self.assertEqual([("u_sync", "clk_pad", "clk_b", 3)], [(d["instance"], d["from"], d["clock"], d["stages"]) for d in dReport["box_synchronizers"]])

    def test_vendor_stubs(self):
        # Without an installation, stub packages of unisim and xpm written from the instances give the same analysis
        dDesign = {
            "top": "vendor_top",
            "vendor_libraries": [{"vendor": "xilinx", "stubs": True}],
            "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "vendor_top.vhd")]}],
            "black_boxes": {
                "IBUF": {"archetype": "buffer", "input": "I", "output": "O"},
                "BUFG": {"archetype": "clock_buffer", "input": "I", "output": "O"},
                "xpm_cdc_single": {
                    "archetype": "synchronizer",
                    "source_clock": "src_clk",
                    "destination_clock": "dest_clk",
                    "input": "src_in",
                    "output": "dest_out",
                    "stages": "DEST_SYNC_FF",
                },
            },
        }
        with tempfile.TemporaryDirectory() as sDirectory:
            dDesign["work_directory"] = os.path.join(sDirectory, "work")
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            sReport = os.path.join(sDirectory, "cdc.json")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign}, oFile)
            dEnvironment = {k: v for k, v in os.environ.items() if k not in ("XILINX_VIVADO", "XILINX_VIVADO_HOME")}
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", "--cdc_report", sReport],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
                env=dEnvironment,
            )
            with open(sReport, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
            self.assertEqual(
                ["unisim.vcomponents.vhd", "xpm.vcomponents.vhd"],
                sorted(os.listdir(os.path.join(sDirectory, "work", "stubs"))),
            )
        self.assertEqual((0, ""), (oResult.returncode, oResult.stdout))
        self.assertEqual([("clk_pad", "port", 1)], [(d["name"], d["kind"], d["registers"]) for d in dReport["clocks"]])
        self.assertEqual([("u_sync", "clk_pad", "clk_b", 3)], [(d["instance"], d["from"], d["clock"], d["stages"]) for d in dReport["box_synchronizers"]])

    def test_stub_package(self):
        # Types, widths and modes come from the actuals; generics an instance leaves out get the first literal
        oDesign = project.from_configuration(
            {
                "design": {
                    "top": "stub_top",
                    "vendor_libraries": [{"library": "vendorlib", "stubs": True}],
                    "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "stub_top.vhd")]}],
                },
            },
        )
        with tempfile.TemporaryDirectory() as sDirectory:
            dFiles = stubs.write(oDesign, sDirectory)
            with open(dFiles["vendorlib"][0], encoding="utf-8") as oFile:
                lLines = oFile.read().splitlines()
        self.assertEqual(dFiles["vendorlib"], oDesign.libraries[0].files)
        self.assertEqual(
            [
                "package components is",
                "  component SHIFTER is",
                "    generic (",
                '      INIT : bit_vector := x"00";',
                "      DEPTH : natural := 2;",
                "      SCALE : real := 1.5;",
                "      ENABLED : boolean := true;",
                '      MODE : string := "fast";',
                "      DELAY : time := 1 ns",
                "    );",
                "    port (",
                "      CLK : in std_logic;",
                "      DIN : in std_logic_vector(3 downto 0);",
                "      SEL : in std_logic;",
                "      LOAD : in std_logic;",
                "      PRESET : in std_logic_vector(3 downto 0);",
                "      COUNT : in std_logic_vector(3 downto 0);",
                "      DOUT : out std_logic_vector(3 downto 0);",
                "      LAST : out std_logic;",
                "      SPARE : out std_logic",
                "    );",
                "  end component;",
                "end package components;",
            ],
            lLines[5:],
        )
        # The design analyzes with the stub: only the missing declaration of the black box is reported
        self.assertEqual(
            [("stub_top.vhd", 42, "design_017", "Black box SHIFTER has no declaration of its clock domain behaviour (2 instances)")],
            self.findings("stub_top", "stub_top.vhd", dDesignKeys={"vendor_libraries": [{"library": "vendorlib", "stubs": True}]}),
        )

    def test_stub_types(self):
        # Comments in the maps are skipped; a function call takes its return type; subtypes and record elements of the
        # design resolve to the types of std_logic_1164; an aggregate that no instance gives a width gets one element;
        # a type the stub cannot declare stands for itself with a comment, and GHDL reports it if it is used
        oDesign = project.from_configuration(
            {
                "design": {
                    "top": "stub_types_top",
                    "vendor_libraries": [{"library": "vendorlib", "stubs": True}],
                    "libraries": [{"name": "work", "files": [os.path.join(sTestDir, "stub_types.vhd")]}],
                },
            },
        )
        with tempfile.TemporaryDirectory() as sDirectory:
            dFiles = stubs.write(oDesign, sDirectory)
            with open(dFiles["vendorlib"][0], encoding="utf-8") as oFile:
                lLines = oFile.read().splitlines()
        self.assertEqual(
            [
                "  component PRIMITIVE is",
                "    generic (",
                "      MODE : string",
                "    );",
                "    port (",
                "      CLK : in std_logic;",
                "      DIN : in std_logic_vector(15 downto 0);",
                "      VALID : in std_logic;",
                "      CASIN : in std_logic_vector(0 downto 0);",
                "      STATE : out std_logic;  -- mode_t cannot be declared here",
                "      DOUT : out std_logic_vector(15 downto 0);",
                "      READY : out std_logic",
                "    );",
                "  end component;",
            ],
            lLines[6:-1],
        )

    def test_stub_directions_from_models(self):
        # Yosys' cell models give the directions of the ports of the primitives they define
        with tempfile.TemporaryDirectory() as sDirectory:
            os.makedirs(os.path.join(sDirectory, "xilinx"))
            with open(os.path.join(sDirectory, "xilinx", "cells.v"), "w", encoding="utf-8") as oFile:
                oFile.write(
                    "module PRIM (...);\n  output [3:0] DO, DRDY;\n  // input FAKE;\n  input wire CLK;\nendmodule\nmodule OTHER (input A);\nendmodule\n",
                )
            self.assertEqual(
                {"PRIM": {"DO": "output", "DRDY": "output", "CLK": "input"}},
                verilog_black_boxes.model_directions(sDirectory, ["xilinx/cells.v"], {"prim"}),
            )

    def test_stub_configuration_errors(self):
        for dEntry, sMessage in (
            ({"library": "unisim", "stubs": True, "files": ["x.vhd"]}, "stubs and files exclude each other"),
            ({"vendor": "lattice", "stubs": True}, "needs family"),
            ({"vendor": "nobody", "stubs": True}, "unknown vendor nobody"),
        ):
            with self.assertRaises(exceptions.ConfigurationError) as oContext:
                vendors.resolve([dEntry], {})
            self.assertIn(sMessage, str(oContext.exception))
        self.assertEqual(["unisim", "xpm"], [o.name for o in vendors.resolve([{"vendor": "xilinx", "stubs": True}], {})])

    def test_stub_positional_association(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFile = os.path.join(sDirectory, "positional.vhd")
            with open(sFile, "w", encoding="utf-8") as oFile:
                oFile.write(
                    "library ieee;\nuse ieee.std_logic_1164.all;\nlibrary unisim;\nuse unisim.vcomponents.all;\n"
                    "entity positional is\n  port (a : in std_logic; y : out std_logic);\nend entity positional;\n"
                    "architecture rtl of positional is\nbegin\n  u_buf : BUFG port map (y, a);\nend architecture rtl;\n",
                )
            oDesign = project.from_configuration(
                {
                    "design": {
                        "top": "positional",
                        "vendor_libraries": [{"library": "unisim", "stubs": True}],
                        "libraries": [{"name": "work", "files": [sFile]}],
                    },
                },
            )
            with self.assertRaises(exceptions.ConfigurationError) as oContext:
                stubs.write(oDesign, sDirectory)
        self.assertIn("instance u_buf of bufg", str(oContext.exception))
        self.assertIn("associates by position", str(oContext.exception))

    def run_library_design(self, sTop, sFile, dVendor, sLibrary):
        dDesign = {
            "top": sTop,
            "vendor_libraries": [dVendor],
            "black_box_libraries": [sLibrary],
            "libraries": [{"name": "work", "files": [os.path.join(sTestDir, sFile)]}],
        }
        with tempfile.TemporaryDirectory() as sDirectory:
            sConfiguration = os.path.join(sDirectory, "design.yaml")
            sReport = os.path.join(sDirectory, "cdc.json")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"design": dDesign}, oFile)
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "--design", "-c", sConfiguration, "-of", "syntastic", "--cdc_report", sReport],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            with open(sReport, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
        lFindings = []
        for sLine in oResult.stdout.splitlines():
            sLocation, sMessage = sLine.split(": ", 1)[1].split(" -- ", 1)
            sFile, sRest = sLocation.rsplit("(", 1)
            sLineNumber, sRule = sRest.split(")", 1)
            lFindings.append((int(sLineNumber), sRule, sMessage))
        return lFindings, dReport

    def test_xilinx_library(self):
        lFindings, dReport = self.run_library_design(
            "xilinx_top",
            "vendor_library_top.vhd",
            {"vendor": "xilinx", "path": os.path.join(sTestDir, "vendor", "vivado")},
            "xilinx",
        )
        # The clock multiplexer, rd_en of the FIFO and port b of the memory with independent clocks cross;
        # the MMCM clock and port b of the memory with a common clock do not
        self.assertEqual(
            [
                (101, "design_008", "mux_q (u_mux.O) captures flag_a (clk_pad) without a synchronizer"),
                (118, "design_008", "u_fifo.rd_en (clk_b) captures en_a (clk_pad) without a synchronizer"),
                (158, "design_008", "u_ram_independent.addrb (clk_b) captures count_a (clk_pad) without a synchronizer"),
            ],
            lFindings,
        )
        self.assertEqual(
            [("clk_pad", "clk_pad", None), ("u_mmcm.CLKOUT0", "clk_pad", "clk_pad"), ("u_mux.O", "u_mux.O", None)],
            [(d["name"], d["group"], d["from"]) for d in dReport["clocks"]],
        )
        self.assertEqual(
            [("u_gray", "synchronizer", 3), ("u_fifo", "dual clock FIFO", None)],
            [(d["instance"], d["kind"], d.get("stages")) for d in dReport["box_synchronizers"]],
        )
        self.assertTrue(all(d["declared_in"] == ["library xilinx"] for d in dReport["black_boxes"]))

    def test_microchip_library(self):
        lFindings, dReport = self.run_library_design(
            "microchip_top",
            "vendor_microchip_top.vhd",
            {"vendor": "microchip", "family": "polarfire", "path": os.path.join(sTestDir, "vendor", "libero")},
            "microchip",
        )
        self.assertEqual(
            [
                (78, "design_017", "Black box SLE: port LAT has no role"),
                (92, "design_008", "u_ram.B_ADDR (clk_b) captures addr_a (clk_pad) without a synchronizer"),
            ],
            lFindings,
        )
        self.assertEqual(
            [("clk_pad", "clk_pad", None), ("u_ccc.OUT0_FABCLK_0", "clk_pad", "clk_pad")],
            [(d["name"], d["group"], d["from"]) for d in dReport["clocks"]],
        )

    def test_assertion_registers(self):
        # The register GHDL makes for an assert of a clocked process is not reported as never changing
        self.assertEqual([], self.findings("assertion_top", "assertion.vhd"))

    def test_automatic_compile_order(self):
        # The files are listed out of order, the package's library last, and order_unused.vhd does not analyze
        sDirectory = os.path.join(sTestDir, "order")
        lFiles = [os.path.join(sDirectory, s) for s in ("order_top.vhd", "order_unused.vhd", "order_leaf.vhd")]
        dLibraries = {"libraries": [{"name": "work", "files": lFiles}, {"name": "util", "files": [os.path.join(sDirectory, "order_pkg.vhd")]}]}
        iStatus, lOutput = self.run_design("order_top", [], dDesignKeys={**dLibraries, "top_library": "work"})
        self.assertEqual(1, iStatus)
        self.assertTrue(any("design_001" in s for s in lOutput))
        iStatus, lOutput = self.run_design("order_top", [], dDesignKeys={**dLibraries, "top_library": "work", "order": "auto"})
        self.assertEqual(0, iStatus, lOutput)
        self.assertFalse(any("design_001" in s for s in lOutput))

    def test_order_must_be_known(self):
        iStatus, lOutput = self.run_design("clean", "clean.vhd", dDesignKeys={"order": "alphabetical"})
        self.assertEqual(1, iStatus)
        self.assertEqual(["ERROR: design order alphabetical is not one of listed, auto"], lOutput)

    def test_crossing_report(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sJson = os.path.join(sDirectory, "cdc.json")
            sText = os.path.join(sDirectory, "cdc.txt")
            sFindings = os.path.join(sDirectory, "findings.json")
            self.run_design("cdc_top", "cdc.vhd", ["--cdc_report", sJson, "--json", sFindings])
            self.run_design("cdc_top", "cdc.vhd", ["--cdc_report", sText])
            with open(sJson, encoding="utf-8") as oFile:
                dReport = json.load(oFile)
            with open(sText, encoding="utf-8") as oFile:
                sReport = oFile.read()
            with open(sFindings, encoding="utf-8") as oFile:
                dFindings = json.load(oFile)
        # The reports record the versions of the tools and the configuration, see docs/lint.rst
        for dRun in (dReport["run"], dFindings["run"]):
            self.assertEqual(version.get_version(), dRun["mhsg"])
            self.assertTrue(dRun["ghdl"] and dRun["yosys"])
            self.assertEqual(64, len(dRun["configuration_files"][0]["sha256"]))
        self.assertIn("\nRun\n  Tools: mhsg ", sReport)
        self.assertIn("  Configuration: ", sReport)
        # --json with --design writes the findings with the keys --json writes for the files of a run
        dFile = next(d for d in dFindings["files"] if d["file_path"].endswith("cdc.vhd"))
        self.assertTrue(all(set(d) == {"rule", "linenumber", "severity", "solution"} for d in dFile["violations"]))
        self.assertTrue(any(d["rule"].startswith("design_") or "cdc" in d["rule"].lower() for d in dFile["violations"]))
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
