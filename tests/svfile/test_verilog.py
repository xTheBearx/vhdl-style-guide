# -*- coding: utf-8 -*-
"""Verilog-2005 files, .v and .vh: read as Verilog-2005, without the rules and advice that need SystemVerilog."""

import os
import re
import subprocess
import sys
import tempfile
import unittest

from mhsg import language, rule_list, rule_set
from mhsg.svFile import svFile

sRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Combinational logic with an incomplete sensitivity list, and always @*, which SystemVerilog writes always_comb
COMBINATIONAL = """\
module comb (
    input wire a_i,
    input wire b_i,
    output reg y_o,
    output reg z_o
);
    always @(a_i) begin
        y_o = a_i & b_i;
    end
    always @* begin
        z_o = a_i;
    end
endmodule
"""


def run(sText, sName, lArguments, dConfig=None):
    """Runs mhsg on a file holding sText; returns (exit status, output lines, text of the file after)."""
    with tempfile.TemporaryDirectory() as sTemporary:
        sFile = os.path.join(sTemporary, sName)
        with open(sFile, "w", encoding="utf-8") as oFile:
            oFile.write(sText)
        lConfig = []
        if dConfig is not None:
            sConfig = os.path.join(sTemporary, "config.yaml")
            with open(sConfig, "w", encoding="utf-8") as oFile:
                oFile.write(dConfig)
            lConfig = ["-c", sConfig]
        oResult = subprocess.run(
            [sys.executable, "bin/mhsg", "-f", sFile, "-of", "syntastic", *lConfig, *lArguments],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        with open(sFile, encoding="utf-8") as oFile:
            sAfter = oFile.read()
    return oResult.returncode, [s.replace(sFile, sName) for s in oResult.stdout.splitlines()] + oResult.stderr.splitlines(), sAfter


V_FILES_SYSTEMVERILOG = "systemverilog:\n  v_files: systemverilog\n"


class test_verilog(unittest.TestCase):
    def test_sensitivity_list_advice(self):
        # Verilog-2005 has no always_comb: the advice of a Verilog file is always @*
        _, lOutput, _ = run(COMBINATIONAL, "comb.v", ["--lint_only", "--rule_set", "none"])
        self.assertIn("ERROR: comb.v(7)sv_lint_008 -- Add b_i to the sensitivity list, or use always @*", lOutput)
        self.assertFalse([s for s in lOutput if "always_comb" in s])
        _, lOutput, _ = run(COMBINATIONAL, "comb.sv", ["--lint_only", "--rule_set", "none"])
        self.assertIn("ERROR: comb.sv(7)sv_lint_008 -- Add b_i to the sensitivity list, or use always_comb", lOutput)
        # As before, with .v files read as SystemVerilog
        _, lOutput, _ = run(COMBINATIONAL, "comb.v", ["--lint_only", "--rule_set", "none"], V_FILES_SYSTEMVERILOG)
        self.assertIn("ERROR: comb.v(7)sv_lint_008 -- Add b_i to the sensitivity list, or use always_comb", lOutput)

    def test_systemverilog_only_rule(self):
        # sv_always_001 asks for always_comb: not applied to a Verilog file, applied to the same text in a .sv file
        _, lOutput, _ = run(COMBINATIONAL, "comb.v", [])
        self.assertFalse([s for s in lOutput if "sv_always_001" in s])
        _, lOutput, _ = run(COMBINATIONAL, "comb.sv", [])
        self.assertIn("ERROR: comb.sv(10)sv_always_001 -- Use always_comb", lOutput)
        _, lOutput, _ = run(COMBINATIONAL, "comb.v", [], V_FILES_SYSTEMVERILOG)
        self.assertIn("ERROR: comb.v(10)sv_always_001 -- Use always_comb", lOutput)

    def test_fix_keeps_verilog(self):
        # The fixes of a Verilog file insert no SystemVerilog: always @* stays, and the file still parses as Verilog
        _, _, sAfter = run(COMBINATIONAL.replace("    always @* begin", "    always @ * begin"), "comb.v", ["--fix"])
        self.assertIn("always @* begin", sAfter)
        self.assertNotIn("always_comb", sAfter)
        _, _, sAfter = run(COMBINATIONAL, "comb.sv", ["--fix"])
        self.assertIn("always_comb begin", sAfter)
        _, _, sAfter = run(COMBINATIONAL, "comb.v", ["--fix"], V_FILES_SYSTEMVERILOG)
        self.assertIn("always_comb begin", sAfter)

    def test_names_that_are_systemverilog_keywords(self):
        # logic and bit are names in Verilog-2005: no syntax error, and the lint rules check the file
        sText = "module names (\n    input wire clk_i,\n    output reg logic\n);\n    wire bit;\n    assign bit = clk_i;\n"
        sText += "    always @(posedge clk_i) begin\n        logic <= bit;\n    end\nendmodule\n"
        iStatus, lOutput, _ = run(sText, "names.v", ["--lint_only", "--rule_set", "none"])
        self.assertEqual([], [s for s in lOutput if "sv_syntax_001" in s])
        self.assertEqual(0, iStatus, lOutput)
        _, lOutput, _ = run(sText, "names.sv", [])
        self.assertTrue([s for s in lOutput if "sv_syntax_001" in s])

    def test_rule_sets(self):
        # The checks of a rule set that name a SystemVerilog only rule do not apply to Verilog files; the others do
        sText = "module latch (\n    input wire en_i,\n    input wire d_i,\n    output reg q_o\n);\n"
        sText += "    always @* begin\n        if (en_i) begin\n            q_o <= d_i;\n        end\n    end\nendmodule\n"
        for sRuleSet in ("do254", "do254_plus", "starc", "cdc"):
            with self.subTest(sRuleSet):
                iStatus, lOutput, _ = run(sText, "latch.v", ["--lint_only", "--rule_set", sRuleSet])
                self.assertFalse([s for s in lOutput if "Traceback" in s or "always_comb" in s or "always_latch" in s], lOutput)
                self.assertIn(iStatus, (0, 1))
        _, lOutput, _ = run(sText, "latch.v", ["--lint_only", "--rule_set", "starc"])
        # STARC 2.2.3.1, no nonblocking assignments in combinational logic, with sv_always_002
        self.assertIn("ERROR: latch.v(8)STARC-2.2.3.1 (sv_always_002) -- Use a blocking assignment (=) in combinational logic", lOutput)

    def test_rules_of_verilog_files(self):
        oFile = svFile(["module m;", "endmodule"], sFilename="m.v")
        setRules = {o.unique_id for o in rule_list.rule_list(oFile, None).rules}
        setSystemVerilog = {o.unique_id for o in rule_list.rule_list(svFile(["module m;", "endmodule"], sFilename="m.sv"), None).rules}
        self.assertEqual(rule_set.systemverilog_only_rules(), frozenset(setSystemVerilog - setRules))
        self.assertIn("sv_lint_008", setRules)
        self.assertIn("sv_always_002", setRules)
        self.assertNotIn("sv_always_001", setRules)
        self.assertTrue(all(language.VERILOG in o.languages for o in rule_list.rule_list(oFile, None).rules))

    def test_verilog_text(self):
        # Rules that apply to both languages give Verilog files advice without SystemVerilog constructs
        sText = "module texts #(\n    parameter Depth = 4,\n    parameter [7:0] Mask = 8'hff\n) (\n    input wire clk_i\n);\n"
        sText += "    reg [7:0] mem [3:0];\nendmodule\n"
        _, lOutput, _ = run(sText, "texts.v", [])
        self.assertIn("ERROR: texts.v(2)sv_declaration_001 -- Give Depth a type, such as integer, or a range", lOutput)
        self.assertFalse([s for s in lOutput if "sv_declaration_001" in s and "Mask" in s])
        self.assertIn("ERROR: texts.v(7)sv_dimension_002 -- Write the unpacked dimension as [0:N-1]", lOutput)
        _, lOutput, _ = run(sText, "texts.v", ["--rule_set", "starc"])
        self.assertIn("WARNING: texts.v(1)STARC-4.1.2.4 (sv_file_006) -- Declare the time unit with `timescale", lOutput)
        _, lOutput, _ = run(sText, "texts.sv", [])
        self.assertIn("ERROR: texts.sv(2)sv_declaration_001 -- Give Depth a type", lOutput)
        self.assertIn("ERROR: texts.sv(3)sv_declaration_001 -- Give Mask a type", lOutput)
        self.assertIn("ERROR: texts.sv(7)sv_dimension_002 -- Write the unpacked dimension as [0:N-1] or [N]", lOutput)


class test_documentation(unittest.TestCase):
    def test_decision_table(self):
        """docs/verilog_2005.rst lists every rule for SystemVerilog once, the SystemVerilog only ones as such."""
        with open(os.path.join(sRoot, "docs", "verilog_2005.rst"), encoding="utf-8") as oFile:
            lRows = re.findall(r"^   \* - :code:`(sv_\w+)`\n     - (.+)$", oFile.read(), re.MULTILINE)
        setRules = {o.unique_id for o in rule_list.load_rules() if o.unique_id.startswith("sv_")}
        self.assertEqual(sorted(setRules), [s for s, _ in lRows])
        self.assertEqual(rule_set.systemverilog_only_rules(), frozenset(s for s, sKind in lRows if sKind == "SystemVerilog only"))
        self.assertEqual({"Both", "Both, Verilog advice", "SystemVerilog only"}, {sKind for _, sKind in lRows})
