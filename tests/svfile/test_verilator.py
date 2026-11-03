# -*- coding: utf-8 -*-
"""Verilator's lint of the SystemVerilog files of a run, see mhsg/svFile/verilator.py and sv_lint_011."""

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
        return [s.replace(sDirectory + os.sep, "") for s in oResult.stdout.splitlines() if "sv_lint_011" in s], oResult.stderr

    def test_findings(self):
        # The package is listed after the file that imports it, and vendor_cell is in no file: Verilator still lints
        lFindings, sErrors = self.run_mhsg(["--lint_only", "--rule_set", "none"])
        self.assertEqual(
            [
                "ERROR: vl_top.sv(16)sv_lint_011 -- Blocking assignment '=' in sequential logic process (Verilator BLKSEQ)",
                "ERROR: vl_top.sv(21)sv_lint_011 -- Non-blocking assignment '<=' in combinational logic process (Verilator COMBDLY)",
                "ERROR: vl_top.sv(25)sv_lint_011 -- Case values incompletely covered (example pattern 0x2) (Verilator CASEINCOMPLETE)",
            ],
            lFindings,
        )
        self.assertEqual("", sErrors)

    def test_rule_set_without_the_rule(self):
        # The DO-254 rule set does not list sv_lint_011; the configuration can enable it
        self.assertEqual([], self.run_mhsg(["--lint_only"])[0])
        lFindings, _ = self.run_mhsg(["--lint"], {"rule": {"sv_lint_011": {"disable": False}}})
        self.assertEqual(3, len(lFindings))

    def test_warnings_option_and_turning_off(self):
        lFindings, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], {"rule": {"sv_lint_011": {"verilator_warnings": ["COMBDLY"]}}})
        self.assertEqual(["vl_top.sv(21)"], [s.split(" ")[1].split("sv_lint")[0] for s in lFindings])
        self.assertEqual([], self.run_mhsg(["--lint_only", "--rule_set", "none"], {"systemverilog": {"verilator": False}})[0])

    def test_files_left_out(self):
        # A file importing a package the run does not define would stop Verilator; it is left out, the others linted
        lFindings, sErrors = self.run_mhsg(["--lint_only", "--rule_set", "none"], lExtra=["vl_uvm_test.sv"])
        self.assertEqual(3, len(lFindings))
        self.assertIn("WARNING: Verilator's checks are left out for 1 file", sErrors)
        self.assertIn("vl_uvm_test.sv", sErrors)
