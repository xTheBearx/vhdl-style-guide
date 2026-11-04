# -*- coding: utf-8 -*-
"""
SystemVerilog files: tokens from slang, kept exactly as written, and the language neutral rules on them.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import pytest

from mhsg import language, parser, rule_list
from mhsg.svFile import svFile, tokens
from mhsg.vhdlFile import vhdlFile

sDirectory = os.path.dirname(os.path.abspath(__file__))
sRoot = os.path.dirname(os.path.dirname(sDirectory))


def read(sName):
    with open(os.path.join(sDirectory, sName), encoding="utf-8") as oFile:
        return oFile.read()


def only(lOutput, *lRuleGroups):
    """The output lines of the rules of the given groups, such as sv_whitespace."""
    return [s for s in lOutput if any(f"){sGroup}_" in s for sGroup in lRuleGroups)]


# Verilator's findings in lint.sv, when it is installed, see sv_lint_011: without a complete sensitivity list,
# Verilator takes the block for a clocked one
VERILATOR_FINDINGS = (
    ["ERROR: lint.sv(21)sv_lint_011 -- Blocking assignment '=' in sequential logic process (Verilator BLKSEQ)"] if shutil.which("verilator") else []
)


class Configuration:
    """A configuration with only a dictionary, as svFile reads it."""

    def __init__(self, dConfig):
        self.dConfig = dConfig


def tokens_of(sText):
    return svFile(sText.splitlines(True), sFilename="test.sv").lAllObjects


class test_language(unittest.TestCase):
    def test_of_file(self):
        for sName in ("a.sv", "a.SVH", "dir/a.v", "a.vh"):
            self.assertEqual(language.SYSTEMVERILOG, language.of_file(sName))
        for sName in ("a.vhd", "a.vhdl", "a.txt", None):
            self.assertEqual(language.VHDL, language.of_file(sName))
        self.assertIs(svFile, language.file_class(language.SYSTEMVERILOG))
        self.assertIs(vhdlFile, language.file_class(language.VHDL))


class test_svfile(unittest.TestCase):
    def test_round_trip(self):
        sText = read("sample.sv")
        oFile = svFile(sText.splitlines(True), sFilename="sample.sv")
        self.assertEqual(sText, "\n".join(oFile.get_lines()[1:]) + "\n")

    def test_generic_tokens(self):
        lTokens = tokens_of("module m; // note\n\n  /* one\n     two */\nendmodule\n")
        self.assertEqual(
            [
                ("ModuleHeader.moduleKeyword", "module"),
                ("whitespace", " "),
                ("ModuleHeader.name", "m"),
                ("ModuleHeader.semi", ";"),
                ("whitespace", " "),
                ("comment", "// note"),
                ("carriage_return", "\n"),
                ("blank_line", ""),
                ("carriage_return", "\n"),
                ("whitespace", "  "),
                ("comment", "/* one"),
                ("carriage_return", "\n"),
                ("whitespace", "     "),
                ("comment", "two */"),
                ("carriage_return", "\n"),
                ("ModuleDeclaration.endmodule", "endmodule"),
                ("carriage_return", "\n"),
            ],
            [(type(o).__name__, o.get_value()) for o in lTokens],
        )

    def test_classification(self):
        lTokens = tokens_of(read("sample.sv"))
        dByValue = {}
        for oToken in lTokens:
            dByValue.setdefault(oToken.get_value(), oToken)
        oName = dByValue["sample"]
        self.assertIsInstance(oName, tokens.of("ModuleHeader", "name"))
        self.assertIsInstance(oName, parser.identifier)
        self.assertEqual("name", oName.field)
        self.assertEqual("ModuleHeader", oName.syntax[-1])
        oAlways = dByValue["always_ff"]
        self.assertIsInstance(oAlways, parser.keyword)
        self.assertEqual("AlwaysFFKeyword", oAlways.kind)
        self.assertEqual("AlwaysFFBlock", oAlways.syntax[-1])
        # Directives and macro uses are kept as written
        self.assertIsInstance(dByValue["`define"], tokens.preprocessor)
        self.assertIsInstance(dByValue["`WIDTH"], tokens.preprocessor)
        # The inactive branch is kept, unclassified
        self.assertIsInstance(dByValue["$display"], tokens.unclassified)

    def test_rules_of_the_language(self):
        oRules = rule_list.rule_list(svFile(["module m;\n", "endmodule\n"], sFilename="m.sv"), None)
        lRules = sorted(o.unique_id for o in oRules.rules)
        self.assertEqual(["length_001", "length_002", "length_004", "whitespace_001", "whitespace_002"], [s for s in lRules if not s.startswith("sv_")])
        self.assertIn("sv_indent_001", lRules)
        self.assertTrue(all(language.SYSTEMVERILOG in o.languages for o in oRules.rules))
        # VHDL files do not get the SystemVerilog rules
        self.assertFalse([o for o in rule_list.rule_list(vhdlFile([""]), None).rules if o.unique_id.startswith("sv_")])
        self.assertGreater(len(rule_list.rule_list(vhdlFile([""]), None).rules), 1000)


@pytest.mark.current_defaults
class test_indent(unittest.TestCase):
    def levels(self, sText):
        """The indent level of the first token of each line, None where indentation is not checked."""
        dReturn = {}
        iLine = 1
        bStart = True
        for oToken in tokens_of(sText):
            if isinstance(oToken, parser.carriage_return):
                iLine += 1
                bStart = True
            elif not isinstance(oToken, (parser.whitespace, parser.blank_line)):
                if bStart:
                    dReturn[iLine] = oToken.get_indent()
                bStart = False
        return [dReturn.get(i) for i in range(1, iLine)]

    def test_levels(self):
        sText = (
            "module m (\n"
            "    input logic a_i\n"
            ");\n"
            "    always_comb begin\n"
            "        if (a_i)\n"
            "            x = 1;\n"
            "        else begin\n"
            "            // comment above end\n"
            "        end\n"
            "        y = f(a,\n"
            "              b);\n"
            "    end\n"
            "endmodule\n"
        )
        self.assertEqual([0, 1, 0, 1, 2, 3, 2, 3, 2, 2, None, 1, 0], self.levels(sText))

    def test_comment_continuing_a_trailing_comment(self):
        sText = "module m;\n    logic a;  // trailing\n              // continued\n    logic b;\nendmodule\n"
        self.assertEqual([0, 1, None, 1, 0], self.levels(sText))

    def test_stacked_comments(self):
        # A comment line under a comment line is not a continuation of a trailing comment
        sText = "module m;\n    initial begin\n        // one\n        // two\n    end\nendmodule\n"
        self.assertEqual([0, 1, 2, 2, 1, 0], self.levels(sText))

    def test_levels_after_utf8(self):
        # slang counts offsets in bytes: a character of several bytes must not shift the lines after it
        sText = "module m; // — em dash\n    logic a;\n    initial begin\n        a = 1;\n    end\nendmodule\n"
        self.assertEqual([0, 1, 1, 2, 1, 0], self.levels(sText))

    def test_zero_width_tokens(self):
        # The implicit type of b_i is a placeholder token of no width at the offset of b_i
        lTokens = tokens_of("module m (input logic [7:0] a_i,b_i);\nendmodule\n")
        oName = [o for o in lTokens if o.get_value() == "b_i"][0]
        self.assertIsInstance(oName, tokens.of("Declarator", "name"))

    def test_token_map_finds_base_classes(self):
        oFile = svFile(["module m;", "    logic a;", "endmodule"], sFilename="m.sv")
        self.assertEqual(["module", "logic", "endmodule"], [o.get_tokens()[0].get_value() for o in oFile.get_tokens_matching([tokens.keyword])])
        self.assertEqual(["m"], [o.get_tokens()[0].get_value() for o in oFile.get_tokens_matching([tokens.of("ModuleHeader", "name")])])


@pytest.mark.current_defaults
class test_rules(unittest.TestCase):
    def run_mhsg(self, lArguments, sFile):
        """
        Runs mhsg on a copy of a test file with the default configuration, not the settings the VHDL test files were
        written for (see tests/test_defaults.yaml); returns (exit status, output lines, file after).
        """
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, sFile)
            shutil.copy(os.path.join(sDirectory, sFile), sCopy)
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sCopy, "-of", "syntastic", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            with open(sCopy, encoding="utf-8") as oFile:
                sAfter = oFile.read()
        return oResult.returncode, [s.replace(sCopy, sFile) for s in oResult.stdout.splitlines()], sAfter

    def test_check(self):
        # The trailing whitespace of line 5 is inside an mhsg_off region
        iStatus, lOutput, _ = self.run_mhsg(["-ap"], "style.sv")
        self.assertEqual(1, iStatus)
        self.assertEqual(
            [
                "ERROR: style.sv(2)sv_indent_001 -- Use 4 spaces for indent",
                "ERROR: style.sv(2)whitespace_001 -- Remove trailing whitespace",
                "ERROR: style.sv(3)whitespace_002 -- Remove tab",
                "ERROR: style.sv(7)sv_whitespace_015 -- Add spaces before the comment",
                "WARNING: style.sv(7)length_001 -- Reduce line to less than 80 characters",
            ],
            sorted(lOutput),
        )

    def test_fix(self):
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "style.sv")
        self.assertEqual(read("style.fixed.sv"), sAfter)
        self.assertEqual(["WARNING: style.sv(7)length_001 -- Reduce line to less than 80 characters"], lOutput)

    def test_block_comment_code_tags(self):
        # /* mhsg_off */ and the other code tags work in block comments as in // comments
        iStatus, lOutput, sAfter = self.run_mhsg(["-ap"], "code_tags.sv")
        self.assertEqual(
            [
                "ERROR: code_tags.sv(12)sv_indent_001 -- Use 4 spaces for indent",
                "ERROR: code_tags.sv(17)sv_indent_001 -- Use 4 spaces for indent",
            ],
            lOutput,
        )
        _, _, sAfter = self.run_mhsg(["--fix"], "code_tags.sv")
        lBefore = read("code_tags.sv").splitlines()
        self.assertEqual([12, 17], [i + 1 for i, sLine in enumerate(sAfter.splitlines()) if sLine != lBefore[i]])

    def test_indent_clean(self):
        self.assertEqual([], only(self.run_mhsg(["-ap"], "indent.sv")[1], "sv_indent", "sv_whitespace"))

    def test_indent_fix(self):
        # Every line whose indent is checked is indented by one space; the fix restores the file
        sText = read("indent.sv")
        lLevels = test_indent.levels(None, sText)
        lLines = sText.splitlines()
        lBad = [" " + sLine.lstrip(" ") if lLevels[i] is not None else sLine for i, sLine in enumerate(lLines)]
        self.assertGreater(sum(1 for i in lLevels if i is not None), 80)
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "indent.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("\n".join(lBad) + "\n")
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix"], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual(sText, oFile.read())

    def test_comment_continuation_follows_its_line(self):
        sText = "module c;\n  logic a;  // trailing\n            // continued\nendmodule\n"
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "c.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write(sText)
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix"], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual("module c;\n    logic a;  // trailing\n              // continued\nendmodule\n", oFile.read())

    def test_whitespace_check(self):
        # The structure rules of phase 1 also report the file; -ap reports the whitespace rules of phase 2 as well
        iStatus, lOutput, _ = self.run_mhsg(["-ap"], "whitespace.sv")
        self.assertEqual(1, iStatus)
        lOutput = only(lOutput, "sv_whitespace")
        lRules = [s.split(")", 1)[1].split(" ")[0] for s in lOutput]
        dCounts = {s: lRules.count(s) for s in lRules}
        self.assertEqual(
            {
                "sv_whitespace_001": 3,
                "sv_whitespace_002": 1,
                "sv_whitespace_003": 1,
                "sv_whitespace_004": 2,
                "sv_whitespace_005": 1,
                "sv_whitespace_006": 2,
                "sv_whitespace_007": 1,
                "sv_whitespace_008": 6,
                "sv_whitespace_009": 1,
                "sv_whitespace_010": 1,
                "sv_whitespace_011": 1,
                "sv_whitespace_012": 1,
                "sv_whitespace_013": 3,
                "sv_whitespace_014": 2,
                "sv_whitespace_015": 1,
            },
            dCounts,
        )

    def test_bracket_spacing(self):
        # No space inside parentheses and the braces of concatenations and assignment patterns, one space in ) (;
        # the braces of a struct and a parenthesis followed by a comment are left alone
        _, lOutput, _ = self.run_mhsg(["-ap"], "brackets.sv")
        lFound = [(int(s.split("(", 1)[1].split(")", 1)[0]), s.split(")", 1)[1].split(" ")[0]) for s in only(lOutput, "sv_whitespace")]
        self.assertEqual(
            [(3, "sv_whitespace_018")]
            + [(9, "sv_whitespace_016")] * 2
            + [(9, "sv_whitespace_017")] * 4
            + [(10, "sv_whitespace_016")] * 2
            + [(15, "sv_whitespace_016")] * 2
            + [(16, "sv_whitespace_016")] * 2,
            sorted(lFound),
        )
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "brackets.sv")
        self.assertEqual(read("brackets.fixed.sv"), sAfter)
        self.assertEqual([], only(lOutput, "sv_whitespace"))

    def test_whitespace_fix(self):
        # The fix keeps the space before the packed dimension of a type, the empty case item, the empty argument,
        # the operators in brackets and the arguments of the macro; it removes the blank lines at the end
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "whitespace.sv")
        self.assertEqual(read("whitespace.fixed.sv"), sAfter)
        self.assertEqual([], only(lOutput, "sv_whitespace", "sv_blank_line"))
        self.assertEqual([], only(self.run_mhsg(["-ap"], "whitespace.fixed.sv")[1], "sv_whitespace", "sv_blank_line"))

    def test_blank_lines_at_end(self):
        self.assertEqual([], only(self.run_mhsg(["-ap"], "whitespace.fixed.sv")[1], "sv_blank_line"))
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "e.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module e;\nendmodule\n\n\n")
            oResult = subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "-of", "syntastic"], cwd=sRoot, capture_output=True, text=True, check=False)
            self.assertEqual([f"ERROR: {sCopy}(3)sv_blank_line_001 -- Remove blank lines at the end of the file"], oResult.stdout.splitlines())

    def test_structure_check(self):
        iStatus, lOutput, _ = self.run_mhsg([], "structure.sv")
        self.assertEqual(1, iStatus)
        self.assertEqual(
            [
                "ERROR: structure.sv(2)sv_generate_005 -- Declare the genvar in the for loop",
                "ERROR: structure.sv(3)sv_module_002 -- Set the parameter in the instantiation instead of with defparam",
                "ERROR: structure.sv(4)sv_always_001 -- Use always_comb",
                "ERROR: structure.sv(4)sv_statement_001 -- Use a begin-end block",
                "ERROR: structure.sv(5)sv_always_001 -- Use always_comb",
                "ERROR: structure.sv(8)sv_always_003 -- Use a nonblocking assignment (<=) in sequential logic",
                "ERROR: structure.sv(8)sv_statement_001 -- Use a begin-end block",
                "ERROR: structure.sv(10)sv_always_002 -- Use a blocking assignment (=) in always_comb",
                "ERROR: structure.sv(10)sv_statement_002 -- Remove the null statement",
                "ERROR: structure.sv(10)sv_statement_002 -- Remove the null statement",
                "ERROR: structure.sv(12)sv_statement_001 -- Use a begin-end block",
                "ERROR: structure.sv(13)sv_module_001 -- Remove the begin-end block from the module",
                "ERROR: structure.sv(15)sv_generate_004 -- Remove generate and endgenerate",
                "ERROR: structure.sv(16)sv_generate_001 -- Label the generate block",
                "ERROR: structure.sv(20)sv_generate_002 -- Rename loop to match (g_|gen_).*",
                "ERROR: structure.sv(21)sv_label_001 -- Change the end label to loop",
                "ERROR: structure.sv(24)sv_always_004 -- Do not mix blocking and nonblocking assignments in an always block",
                "ERROR: structure.sv(29)sv_always_003 -- Use a nonblocking assignment (<=) in sequential logic",
                "ERROR: structure.sv(33)sv_case_001 -- Add a default item",
                "ERROR: structure.sv(46)sv_label_001 -- Remove the end label, the block has no begin label",
            ],
            lOutput,
        )

    def test_structure_fix(self):
        # The fixes change always @* to always_comb, <= to = in always_comb, remove null statements, the generate
        # region and the end label without a begin label, and correct the mismatched end label
        _, _, sAfter = self.run_mhsg(["--fix"], "structure.sv")
        self.assertEqual(read("structure.fixed.sv"), sAfter)

    def run_with_configuration(self, sConfiguration, sFile):
        with tempfile.TemporaryDirectory() as sTemporary:
            sConfigurationFile = os.path.join(sTemporary, "c.yaml")
            with open(sConfigurationFile, "w", encoding="utf-8") as oFile:
                oFile.write(sConfiguration)
            return self.run_mhsg(["-c", sConfigurationFile], sFile)

    def test_waive_for_locals(self):
        _, lOutput, _ = self.run_with_configuration("rule:\n  sv_always_003:\n    waive_for_locals: yes\n", "structure.sv")
        self.assertNotIn("ERROR: structure.sv(29)sv_always_003 -- Use a nonblocking assignment (<=) in sequential logic", lOutput)
        self.assertIn("ERROR: structure.sv(8)sv_always_003 -- Use a nonblocking assignment (<=) in sequential logic", lOutput)

    def test_generate_label_pattern(self):
        _, lOutput, _ = self.run_with_configuration("rule:\n  sv_generate_002:\n    pattern: '(loop|gen_).*'\n", "structure.sv")
        self.assertFalse([s for s in lOutput if "sv_generate_002" in s])

    def test_one_statement_per_line(self):
        _, lOutput, _ = self.run_with_configuration("rule:\n  sv_statement_003:\n    disable: false\n", "structure.sv")
        self.assertIn("ERROR: structure.sv(43)sv_statement_003 -- Move the statement to its own line", lOutput)
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "s.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module s;\n    always_comb begin\n        a = 1; b = 2;\n    end\nendmodule\n")
            sConfigurationFile = os.path.join(sTemporary, "c.yaml")
            with open(sConfigurationFile, "w", encoding="utf-8") as oFile:
                oFile.write("rule:\n  sv_statement_003:\n    disable: false\n")
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix", "-c", sConfigurationFile], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual("module s;\n    always_comb begin\n        a = 1;\n        b = 2;\n    end\nendmodule\n", oFile.read())

    def test_declarations_check(self):
        # Every rule enabled, see all_rules.yaml; the indent, whitespace and begin-end rules are left out
        _, lOutput, _ = self.run_mhsg(["-ap", "-c", os.path.join(sDirectory, "all_rules.yaml")], "declarations.sv")
        lOutput = [s.split(" ", 1)[1] for s in lOutput if not any(x in s for x in ("sv_indent", "sv_whitespace", "sv_statement_001", "sv_alignment"))]
        self.assertEqual(
            [
                "declarations.sv(1)sv_naming_005 -- Rename macro data_width to match [A-Z_0-9]+",
                "declarations.sv(3)sv_file_004 -- Use a relative path in `include",
                "declarations.sv(4)sv_file_002 -- Name the file after package types",
                "declarations.sv(5)sv_naming_002 -- Rename State to match [a-z_0-9]+(_t|_e)",
                "declarations.sv(6)sv_naming_003 -- Rename Beat to match [a-z_0-9]+_t",
                "declarations.sv(10)sv_declaration_001 -- Give data_width a type",
                "declarations.sv(10)sv_literal_003 -- Write the parameter value with a base, such as 'd",
                "declarations.sv(10)sv_naming_001 -- Rename parameter data_width to match ([A-Z0-9]+[a-z0-9]*)+(_[0-9]+)?|[A-Z_0-9]+",
                "declarations.sv(11)sv_literal_003 -- Write the parameter value with a base, such as 'd",
                "declarations.sv(11)sv_naming_007 -- Rename DisableParity after what it enables",
                "declarations.sv(14)sv_dimension_001 -- Write the packed dimension as [msb:lsb]",
                "declarations.sv(15)sv_naming_008 -- Rename Valid_o to match [a-z_0-9]+",
                "declarations.sv(17)sv_literal_003 -- Write the parameter value with a base, such as 'd",
                "declarations.sv(17)sv_naming_001 -- Rename localparam MAX_COUNT to match ([A-Z0-9]+[a-z0-9]*)+(_[0-9]+)?",
                "declarations.sv(19)sv_dimension_002 -- Write the unpacked dimension as [0:N-1] or [N]",
                "declarations.sv(21)sv_naming_010 -- Rename signal, a VHDL keyword",
                "declarations.sv(22)sv_naming_011 -- Rename vdd_ok, which starts like a power net",
                "declarations.sv(23)sv_naming_008 -- Rename Data to match [a-z_0-9]+",
                "declarations.sv(23)sv_naming_012 -- Rename Data, which differs from data only in case",
                "declarations.sv(24)sv_naming_013 -- Use 2 to 40 characters for signal v",
                "declarations.sv(25)sv_naming_009 -- Use only letters, digits and underscores in _x, starting with a letter",
                "declarations.sv(26)sv_typedef_001 -- Declare the enum type with typedef",
                "declarations.sv(27)sv_typedef_002 -- Declare the struct or union type with typedef",
                "declarations.sv(28)sv_literal_001 -- Write all 4 digits of the binary literal",
                "declarations.sv(29)sv_literal_002 -- The value needs 8 bits, more than the width 4",
                "declarations.sv(31)sv_literal_004 -- Give the literal a width; it needs more than 32 bits",
                "declarations.sv(32)sv_function_001 -- Declare the function automatic or static",
                "declarations.sv(32)sv_function_003 -- Give argument data a type",
                "declarations.sv(33)sv_function_004 -- Use a blocking assignment (=) in a function",
                "declarations.sv(35)sv_function_002 -- Declare the task automatic or static",
                "declarations.sv(35)sv_function_005 -- Use a function instead of a task",
                "declarations.sv(35)sv_naming_013 -- Use 2 to 40 characters for port n",
                "declarations.sv(37)sv_naming_013 -- Use 2 to 40 characters for port d",
                "declarations.sv(40)sv_statement_004 -- Remove the initial block from design code",
                "declarations.sv(42)sv_literal_005 -- Do not compare with x or z",
                "declarations.sv(43)sv_always_006 -- Move the statement to an always block of its own",
                "declarations.sv(44)sv_always_006 -- Move the statement to an always block of its own",
                "declarations.sv(44)sv_case_003 -- Use a signal as the case selector, not a constant",
                "declarations.sv(45)sv_statement_006 -- Remove the empty branch or give it a statement",
                "declarations.sv(50)sv_always_005 -- Use a single event control, at the start of the always block",
                "declarations.sv(52)sv_comment_001 -- Remove the synthesis directive from the comment",
                "declarations.sv(56)sv_file_003 -- Move the module to a file of its own",
                "declarations.sv(58)sv_naming_004 -- Rename Bus to match [a-z_0-9]+_if",
                "declarations.sv(58)sv_naming_010 -- Rename Bus, a VHDL keyword",
                "declarations.sv(61)sv_naming_013 -- Use 2 to 40 characters for signal x",
                "declarations.sv(62)sv_naming_006 -- Rename Length to match ([a-z0-9]+_)+c",
            ],
            lOutput,
        )

    def test_declarations_fix(self):
        _, _, sAfter = self.run_mhsg(["--fix"], "declarations.sv")
        lAfter = sAfter.splitlines()
        self.assertIn("    function automatic logic parity(input data);", lAfter)
        self.assertIn("    task automatic wait_cycles(input int n);", lAfter)
        self.assertIn("    assign v = 4'b0001;", lAfter)
        # A function already automatic, and zero, are left as they are
        self.assertIn("    function automatic logic ok(input logic [7:0] d);", lAfter)
        self.assertIn("    assign v = 4'b0;", lAfter)

    def test_syntax_errors(self):
        # The rules on constructs skip a file slang cannot parse; sv_syntax_001 reports the error. A macro
        # defined in another file is not an error.
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "e.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module e;\n    always @* y = a +;\n    `UNDEFINED(x)\nendmodule\n")
            oResult = subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "-of", "syntastic"], cwd=sRoot, capture_output=True, text=True, check=False)
        self.assertEqual([f"ERROR: {sCopy}(2)sv_syntax_001 -- Syntax error: expected expression"], oResult.stdout.splitlines())

    def test_lint(self):
        _, lOutput, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], "lint.sv")
        self.assertEqual(
            [
                "ERROR: lint.sv(13)sv_lint_005 -- Variable 'spare' is assigned but its value is never used",
                "ERROR: lint.sv(14)sv_lint_001 -- Implicit conversion truncates from 8 to 4 bits",
                "ERROR: lint.sv(16)sv_lint_002 -- Latch inferred for 'l_o' because it is not assigned on all control paths",
                "ERROR: lint.sv(19)sv_lint_003 -- Cannot mix continuous and procedural assignments to variable 'm_o'",
                "ERROR: lint.sv(20)sv_lint_004 -- Implicit net 'implicit_net' created",
                "ERROR: lint.sv(20)sv_lint_005 -- Implicit net 'implicit_net' is unused elsewhere",
                "ERROR: lint.sv(21)sv_lint_008 -- Add b_i to the sensitivity list, or use always_comb",
                *VERILATOR_FINDINGS,
                "ERROR: lint.sv(25)sv_lint_006 -- 'case' statement contains duplicate items for value '4'b1' (the second one will never be matched)",
                "ERROR: lint.sv(30)sv_lint_007 -- Comparison of differently signed types ('logic[3:0]' and 'int')",
            ],
            lOutput,
        )

    def test_sensitivity_list(self):
        # The signals gate and twice read count for the first block; q, which copy writes first, the member of cfg and
        # the package item do not count for the second; the hierarchical name counts for the third
        _, lOutput, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], "sensitivity.sv")
        self.assertEqual(
            [
                "ERROR: sensitivity.sv(29)sv_lint_008 -- Add b_i, c_i to the sensitivity list, or use always_comb",
                "ERROR: sensitivity.sv(38)sv_lint_008 -- Add u_sub.valid to the sensitivity list, or use always_comb",
            ],
            [s for s in lOutput if "sv_lint_008" in s],
        )

    def test_lint_do254(self):
        # The default rule set of lint mode labels the SystemVerilog rules with the DO-254 checks they implement
        _, lOutput, _ = self.run_mhsg(["--lint_only"], "lint.sv")
        self.assertIn("WARNING: lint.sv(16)DO254-SS4 (sv_lint_002) -- Latch inferred for 'l_o' because it is not assigned on all control paths", lOutput)
        self.assertIn("ERROR: lint.sv(19)DO254-SS6 (sv_lint_003) -- Cannot mix continuous and procedural assignments to variable 'm_o'", lOutput)

    def test_lint_file_using_other_files(self):
        # A file using a module, package or macro of another file is not checked for undriven, unused or implicit
        # signals: one driven or read there would look undriven or unused
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "top.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module top (input logic a_i, output logic y_o);\n    logic spare;\n    sub u_sub (.a(a_i), .y(y_o));\nendmodule\n")
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sCopy, "-of", "syntastic", "--lint_only", "--rule_set", "none"],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual([], oResult.stdout.splitlines())

    def run_project(self, lFiles, lArguments):
        lPaths = [os.path.join(sDirectory, "project", s) for s in lFiles]
        oResult = subprocess.run(
            [sys.executable, "bin/mhsg", "-f", *lPaths, "-of", "syntastic", "-c", os.path.join(sDirectory, "project", "project.yaml"), *lArguments],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        return [s.replace(os.path.join(sDirectory, "project") + os.sep, "") for s in oResult.stdout.splitlines()]

    def test_lint_of_the_run(self):
        # Compiled together, the files are checked against each other: the instance against the module
        self.assertEqual(
            [
                "ERROR: top.sv(9)sv_lint_005 -- Unused variable 'spare'",
                "ERROR: top.sv(11)sv_lint_009 -- Output port 'unused_o' has no connection (slang UnconnectedOutputPort)",
                "ERROR: top.sv(13)sv_lint_001 -- Implicit conversion of port connection truncates from 8 to 4 bits",
                "ERROR: top.sv(18)sv_lint_005 -- Unused variable 'extra'",
                "ERROR: sub.sv(5)sv_lint_010 -- Undriven output port 'unused_o'",
            ],
            self.run_project(["top.sv", "sub.sv"], ["--lint_only", "--rule_set", "none"]),
        )

    def test_lint_of_a_file_alone(self):
        # Alone, top.sv uses a module the run does not know, so unused and undriven signals are not checked
        self.assertEqual([], self.run_project(["top.sv"], ["--lint_only", "--rule_set", "none"]))

    def test_preprocessor_settings(self):
        # The include directory and the define of the configuration: `WIDTH expands and the ifdef branch is parsed
        lOutput = self.run_project(["top.sv", "sub.sv"], ["-ap"])
        self.assertFalse([s for s in lOutput if "sv_syntax_001" in s])
        oFile = svFile(
            read(os.path.join("project", "top.sv")).splitlines(True),
            sFilename=os.path.join(sDirectory, "project", "top.sv"),
            configuration=Configuration(
                {"systemverilog": {"defines": {"EXTRA": None}, "include_directories": [os.path.join(sDirectory, "project", "include")]}},
            ),
        )
        self.assertIsInstance([o for o in oFile.lAllObjects if o.get_value() == "extra"][0], tokens.of("Declarator", "name"))

    def test_alignment(self):
        # The ports, declarations and named connections were aligned by their author and are aligned again; the
        # localparams were nearly flush left and are made flush left; the assignments and case items are in
        # between, with 3 spaces too many, and are left as they are
        _, lOutput, _ = self.run_mhsg(["-ap"], "alignment.sv")
        self.assertEqual(
            [
                "ERROR: alignment.sv(4)sv_alignment_001 -- Align valid_o in column 24",
                "ERROR: alignment.sv(7)sv_alignment_006 -- Use 1 space(s) before =",
                "ERROR: alignment.sv(8)sv_alignment_004 -- Align valid in column 18",
                "ERROR: alignment.sv(9)sv_alignment_004 -- Align data in column 18",
                "ERROR: alignment.sv(10)sv_alignment_004 -- Align wide in column 18",
                "ERROR: alignment.sv(16)sv_alignment_002 -- Align ( in column 19",
            ],
            only(lOutput, "sv_alignment"),
        )
        _, _, sAfter = self.run_mhsg(["--fix"], "alignment.sv")
        self.assertEqual(read("alignment.fixed.sv"), sAfter)

    def test_alignment_policies(self):
        _, lOutput, _ = self.run_with_configuration("rule:\n  sv_alignment_005:\n    policy: align\n", "alignment.sv")
        self.assertIn("ERROR: alignment.sv(12)sv_alignment_005 -- Align = in column 20", lOutput)
        _, lOutput, _ = self.run_with_configuration("rule:\n  sv_alignment_005:\n    policy: flush_left\n", "alignment.sv")
        self.assertIn("ERROR: alignment.sv(11)sv_alignment_005 -- Use 1 space(s) before =", lOutput)

    def test_sample_is_clean(self):
        self.assertEqual((0, []), self.run_mhsg([], "sample.sv")[:2])
