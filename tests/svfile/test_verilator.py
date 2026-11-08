# -*- coding: utf-8 -*-
"""Verilator's lint of the Verilog and SystemVerilog files of a run, see mhsg/svFile/verilator.py and sv_lint_011."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from pyslang.syntax import SyntaxTree  # pylint: disable=import-error

from mhsg.svFile import verilator

sDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verilator")
sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def tree(sText):
    return SyntaxTree.fromText(sText)


class test_verilator(unittest.TestCase):
    def test_packages_first(self):
        lFiles = [
            ("top.sv", tree("module top import b_pkg::*; (); endmodule")),
            ("b_pkg.sv", tree("package b_pkg; localparam int W = a_pkg::W; endpackage")),
            ("other.sv", tree("module other; endmodule")),
            ("a_pkg.sv", tree("package a_pkg; localparam int W = 4; endpackage")),
        ]
        self.assertEqual(["a_pkg.sv", "b_pkg.sv", "top.sv", "other.sv"], [s for s, _ in verilator.compile_order(lFiles)])

    def test_hierarchical_names_are_not_packages(self):
        # u_report.check calls a task of an instance; p_pkg::W uses a package (issue 88)
        oTree = tree(
            "module tb; rep u_report(); initial begin u_report.check(1'b1); x = p_pkg::W; end endmodule module rep; task check(input ok); endtask endmodule",
        )
        self.assertEqual((set(), {"p_pkg"}), verilator.packages(oTree))
        oBench = tree("module tb; rep u_report(); initial u_report.check(1'b1); endmodule module rep; task check(input ok); endtask endmodule")
        self.assertEqual(["tb.v"], [s for s, _ in verilator.without_unknown_packages([("tb.v", oBench)])])

    def test_stubs_for_unknown_modules(self):
        lTrees = [tree("module top; logic a; known u0 (); vcell #(.W(8)) u1 (.x(a), .y()); prim #(2) u2 (a, a); endmodule"), tree("module known; endmodule")]
        self.assertEqual(
            "module prim #(parameter mhsg_parameter_0 = 0) (input wire mhsg_port_0, input wire mhsg_port_1);\nendmodule\n"
            "module vcell #(parameter W = 0) (input wire x, input wire y);\nendmodule\n",
            verilator.stubs(lTrees),
        )

    def test_offset_counts_bytes(self):
        sText = "// é\nlogic a;\n"
        self.assertEqual(len("// é\n".encode("utf-8")) + 6, verilator.offset(sText, verilator.line_starts(sText), 2, 7))
        self.assertIsNone(verilator.offset(sText, verilator.line_starts(sText), 9, 1))

    def test_timing_option(self):
        # Verilator 5 lints the timing controls of testbenches with --timing; Verilator 4 knows neither option
        for sVersion in ("Verilator 5.020 2024-01-01 rev (Debian 5.020-1)", "Verilator 5.032 2025-01-01 rev v5.032", "Verilator 6.000"):
            lCommand = verilator.command("verilator", ["/rtl/a.sv"], {}, None, sVersion)
            self.assertIn("--timing", lCommand)
            self.assertNotIn("--no-timing", lCommand)
        for sVersion in ("Verilator 4.038 2020-07-11 rev v4.036-114-g0cd4a57ad", None, "something else"):
            lCommand = verilator.command("verilator", ["/rtl/a.sv"], {}, None, sVersion)
            self.assertNotIn("--timing", lCommand)
            self.assertNotIn("--no-timing", lCommand)

    def test_verilog_files_as_verilog_2005(self):
        lPaths = ["/rtl/a.v", "/rtl/b.sv", "/rtl/c.vh", "/rtl/d.v"]
        lCommand = verilator.command("verilator", lPaths, {}, "/tmp/mhsg_stubs.sv", "Verilator 5.020")
        self.assertEqual(["+1364-2005ext+v", "+1364-2005ext+vh"], [s for s in lCommand if s.startswith("+1364")])
        self.assertEqual(lPaths, lCommand[-len(lPaths) :])
        # A project writing SystemVerilog in .v files
        lCommand = verilator.command("verilator", lPaths, {"systemverilog": {"v_files": "systemverilog"}}, None, "Verilator 5.020")
        self.assertEqual([], [s for s in lCommand if s.startswith("+1364")])
        self.assertEqual([], [s for s in verilator.command("verilator", ["/rtl/b.sv"], {}, None, "Verilator 5.020") if s.startswith("+1364")])

    def test_turned_off(self):
        self.assertIsNone(verilator.find({"systemverilog": {"verilator": False}}))
        self.assertIsNone(verilator.find({"systemverilog": {"verilator": "/no/such/verilator"}}))


@unittest.skipUnless(shutil.which("verilator"), "Verilator is not installed")
class test_verilator_lint(unittest.TestCase):
    def run_mhsg(self, lArguments, dConfiguration=None, lExtra=()):
        with tempfile.TemporaryDirectory() as sTemporary:
            lConfiguration = []
            if dConfiguration is not None:
                sConfiguration = os.path.join(sTemporary, "mhsg.json")
                with open(sConfiguration, "w", encoding="utf-8") as oFile:
                    json.dump(dConfiguration, oFile)
                lConfiguration = ["-c", sConfiguration]
            lFiles = [os.path.join(sDirectory, s) for s in ("vl_top.sv", "vl_pkg.sv", *lExtra)]
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", *lFiles, "-of", "syntastic", *lConfiguration, *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        return [s.replace(sDirectory + os.sep, "") for s in oResult.stdout.splitlines() if "Verilator" in s], oResult.stderr

    def test_findings(self):
        # The package is listed after the file that imports it, and vendor_cell is in no file: Verilator still lints
        lFindings, sErrors = self.run_mhsg(["--lint_only", "--rule_set", "none"])
        self.assertEqual(
            [
                "ERROR: vl_top.sv(16)sv_lint_011 -- Blocking assignment '=' in sequential logic process (Verilator BLKSEQ)",
                "ERROR: vl_top.sv(21)sv_lint_011 -- Non-blocking assignment '<=' in combinational logic process (Verilator COMBDLY)",
                "ERROR: vl_top.sv(25)sv_lint_013 -- Case values incompletely covered (example pattern 0x2) (Verilator CASEINCOMPLETE)",
            ],
            lFindings,
        )
        self.assertEqual("", sErrors)

    def test_rule_sets(self):
        # The DO-254 rule set lists sv_lint_013 under SS2 but not sv_lint_011; the configuration can enable it
        self.assertEqual(
            ["ERROR: vl_top.sv(25)DO254-SS2 (sv_lint_013) -- Case values incompletely covered (example pattern 0x2) (Verilator CASEINCOMPLETE)"],
            self.run_mhsg(["--lint_only"])[0],
        )
        lFindings, _ = self.run_mhsg(["--lint"], {"rule": {"sv_lint_011": {"disable": False}}})
        self.assertEqual(3, len(lFindings))

    def test_warnings_option_and_turning_off(self):
        lFindings, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], {"rule": {"sv_lint_011": {"verilator_warnings": ["COMBDLY"]}}})
        # The option is sv_lint_011's; sv_lint_013 still reports CASEINCOMPLETE
        self.assertEqual(["vl_top.sv(21)"], [s.split(" ")[1].split("sv_lint")[0] for s in lFindings if "sv_lint_011" in s])
        self.assertEqual([], self.run_mhsg(["--lint_only", "--rule_set", "none"], {"systemverilog": {"verilator": False}})[0])

    def test_verilog_testbench(self):
        # Verilator 5 lints the timing controls of a Verilog testbench with --timing, and reads the file as
        # Verilog-2005, where logic is a name: the file is not left out
        lFindings, sErrors = self.run_mhsg(["--lint_only", "--rule_set", "none"], lExtra=["vl_tb.v"])
        self.assertEqual("", sErrors)
        self.assertIn("ERROR: vl_tb.v(10)sv_lint_011 -- Non-blocking assignment '<=' in initial/final block (Verilator INITIALDLY)", lFindings)

    def test_files_left_out(self):
        # A file importing a package the run does not define would stop Verilator; it is left out, the others linted
        lFindings, sErrors = self.run_mhsg(["--lint_only", "--rule_set", "none"], lExtra=["vl_uvm_test.sv"])
        self.assertEqual(3, len(lFindings))
        self.assertIn("WARNING: Verilator's checks are left out for 1 file", sErrors)
        self.assertIn("vl_uvm_test.sv", sErrors)
