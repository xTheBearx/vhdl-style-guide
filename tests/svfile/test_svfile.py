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

from mhsg import exceptions, language, parser, rule_list
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
        for sName in ("a.sv", "a.SVH"):
            self.assertEqual(language.SYSTEMVERILOG, language.of_file(sName))
        for sName in ("dir/a.v", "a.vh", "a.V"):
            self.assertEqual(language.VERILOG, language.of_file(sName))
            # A project writing SystemVerilog in .v files reads them so
            self.assertEqual(language.SYSTEMVERILOG, language.of_file(sName, {"systemverilog": {"v_files": "systemverilog"}}))
            self.assertTrue(language.is_verilog(sName))
        for sName in ("a.vhd", "a.vhdl", "a.txt", None):
            self.assertEqual(language.VHDL, language.of_file(sName))
            self.assertFalse(language.is_verilog(sName))
        self.assertIs(svFile, language.file_class(language.SYSTEMVERILOG))
        self.assertIs(svFile, language.file_class(language.VERILOG))
        self.assertIs(vhdlFile, language.file_class(language.VHDL))

    def test_verilog_2005_names(self):
        # logic and bit are names in Verilog-2005, keywords only in SystemVerilog
        lText = ["module m (input wire clk);", "    reg logic;", "    wire bit;", "    always @(posedge clk) logic <= bit;", "endmodule"]
        oFile = svFile(lText, sFilename="names.v")
        self.assertEqual(language.VERILOG, oFile.language)
        self.assertEqual([], oFile.syntax_errors)
        self.assertEqual([], [o for o in oFile.lAllObjects if isinstance(o, tokens.unclassified)])
        self.assertIsInstance([o for o in oFile.lAllObjects if o.get_value() == "logic"][0], tokens.of("Declarator", "name"))
        # The same text in a .sv file, or in a .v file read as SystemVerilog, is not SystemVerilog
        oFile = svFile(lText, sFilename="names.sv")
        self.assertEqual(language.SYSTEMVERILOG, oFile.language)
        self.assertIn("ExpectedDeclarator", [s for _, s in oFile.syntax_errors])
        oFile = svFile(lText, sFilename="names.v", configuration=Configuration({"systemverilog": {"v_files": "systemverilog"}}))
        self.assertEqual(language.SYSTEMVERILOG, oFile.language)
        self.assertIn("ExpectedDeclarator", [s for _, s in oFile.syntax_errors])
        # With defines, a Verilog file is still read as Verilog-2005
        oFile = svFile(lText, sFilename="names.v", configuration=Configuration({"systemverilog": {"defines": {"SYNTHESIS": None}}}))
        self.assertEqual([], oFile.syntax_errors)

    def test_v_files_setting(self):
        self.assertEqual(language.VERILOG, language.v_files({}))
        self.assertEqual(language.VERILOG, language.v_files({"systemverilog": {"defines": {"A": None}}}))
        self.assertEqual(language.SYSTEMVERILOG, language.v_files({"systemverilog": {"v_files": "SystemVerilog"}}))
        with self.assertRaises(exceptions.ConfigurationError):
            language.v_files({"systemverilog": {"v_files": "vhdl"}})


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

    def test_macro_arguments(self):
        # The arguments of a macro use are classified where the macro places them, and the body of the definition
        # where its use places it, so both are checked
        sText = "`define CHECK(name, cond) assert property (@(posedge clk) cond);\nmodule m (input logic clk, a, b);\n    `CHECK(eq, a==b)\nendmodule\n"
        lTokens = tokens_of(sText)
        lEquals = [o for o in lTokens if o.get_value() == "=="]
        self.assertEqual(1, len(lEquals))
        self.assertTrue(lEquals[0].macro_argument)
        self.assertIsInstance(lEquals[0], tokens.of("EqualityExpression", "operatorToken"))
        oAssert = [o for o in lTokens if o.get_value() == "assert"][0]
        self.assertIsInstance(oAssert, tokens.of("AssertPropertyStatement", "keyword"))
        self.assertTrue(oAssert.macro_body)

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
        # The code of the inactive branch is classified as where the branch is active, and marked inactive
        self.assertIsInstance(dByValue["$display"], tokens.of("SystemName", "systemIdentifier"))
        self.assertTrue(dByValue["$display"].inactive)

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

    def test_continuation_lines(self):
        # Only the continuation lines at or left of their statement are reported: the aligned arguments, the closing
        # bracket, the line after the attribute and the next expression of the case item are not. The arguments of the
        # call whose ( ends its line are sv_indent_004's
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "continuation.sv")
        self.assertEqual(read("continuation.fixed.sv"), sAfter)
        _, lOutput, _ = self.run_mhsg(["-ap"], "continuation.sv")
        self.assertEqual(
            [
                "ERROR: continuation.sv(9)sv_indent_002 -- Indent the continuation line by 8 spaces",
                "ERROR: continuation.sv(17)sv_indent_004 -- Indent the line of the list by 12 spaces",
            ],
            only(lOutput, "sv_indent"),
        )

    def test_directives(self):
        # Conditional directives at column 0, as Verible puts them; the others and macro calls at the level of the code
        # around them, one in before end and endmodule; the line a `define continues is left alone
        _, lOutput, _ = self.run_mhsg(["-ap"], "directives.sv")
        self.assertEqual(
            [
                "ERROR: directives.sv(2)sv_indent_003 -- Start the directive at column 0",
                "ERROR: directives.sv(13)sv_indent_003 -- Start the directive at column 0",
                "ERROR: directives.sv(15)sv_indent_003 -- Start the directive at column 0",
                "ERROR: directives.sv(17)sv_indent_003 -- Start the directive at column 0",
                "ERROR: directives.sv(18)sv_indent_003 -- Indent the directive by 8 spaces",
                "ERROR: directives.sv(20)sv_indent_003 -- Indent the directive by 4 spaces",
                "ERROR: directives.sv(22)sv_indent_003 -- Indent the directive by 4 spaces",
            ],
            only(lOutput, "sv_indent"),
        )
        _, _, sAfter = self.run_mhsg(["--fix"], "directives.sv")
        self.assertEqual(read("directives.fixed.sv"), sAfter)
        self.assertEqual([], only(self.run_mhsg(["-ap"], "directives.fixed.sv")[1], "sv_indent"))

    def test_conditional_directives_indented_like_code(self):
        with tempfile.TemporaryDirectory() as sTemporary:
            sConfiguration = os.path.join(sTemporary, "config.yaml")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                oFile.write("rule:\n  sv_indent_003:\n    conditional_indent: code\n")
            _, lOutput, _ = self.run_mhsg(["-ap", "-c", sConfiguration], "directives.fixed.sv")
        self.assertEqual(
            [
                "ERROR: directives.fixed.sv(13)sv_indent_003 -- Indent the directive by 8 spaces",
                "ERROR: directives.fixed.sv(15)sv_indent_003 -- Indent the directive by 8 spaces",
                "ERROR: directives.fixed.sv(17)sv_indent_003 -- Indent the directive by 8 spaces",
            ],
            only(lOutput, "sv_indent"),
        )

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

    def test_alignment_columns(self):
        # The types after the directions, then the packed dimensions, are aligned before the names; a port without a
        # type and a declaration without a dimension stay in their groups. The dimension of b_o is in its column until
        # the fix moves the types
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "columns.sv")
        self.assertEqual(read("columns.fixed.sv"), sAfter)
        _, lOutput, _ = self.run_mhsg(["-ap"], "columns.sv")
        self.assertEqual(
            [
                "ERROR: columns.sv(2)sv_alignment_009 -- Align logic in column 12",
                "ERROR: columns.sv(3)sv_alignment_009 -- Align logic in column 12",
                "ERROR: columns.sv(9)sv_alignment_010 -- Align [ in column 11",
                "ERROR: columns.sv(11)sv_alignment_010 -- Align [ in column 11",
            ],
            only(lOutput, "sv_alignment"),
        )

    def test_alignment_inside_dimensions(self):
        # The packed dimensions aligned in a column are aligned too, each aligned right inside its brackets by spaces
        # after the bracket, as Verible does; a dimension much wider than the others leaves them flush left
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "dimensions.sv")
        self.assertEqual(read("dimensions.fixed.sv"), sAfter)
        _, lOutput, _ = self.run_mhsg(["-ap"], "dimensions.sv")
        self.assertEqual(
            [
                "ERROR: dimensions.sv(3)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
                "ERROR: dimensions.sv(7)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
                "ERROR: dimensions.sv(9)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
                "ERROR: dimensions.sv(14)sv_alignment_011 -- Use 2 space(s) after [ to align the dimension",
                "ERROR: dimensions.sv(14)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
                "ERROR: dimensions.sv(15)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
            ],
            only(lOutput, "sv_alignment"),
        )
        self.assertEqual([], only(self.run_mhsg(["-ap"], "dimensions.fixed.sv")[1], "sv_alignment"))

    def test_assignment_pattern_indent(self):
        # The elements of a pattern whose '{ ends its line are one level in from that line and the } at it, as Verible
        # lays them out; a nested pattern from the line of its own '{; a continuous assign one level more; a pattern
        # written on the line of its '{ is left alone
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "patterns.sv")
        self.assertEqual(read("patterns.fixed.sv"), sAfter)
        _, lOutput, _ = self.run_mhsg(["-ap"], "patterns.sv")
        self.assertEqual(13, len([s for s in lOutput if ")sv_indent_004 " in s]))
        self.assertIn("ERROR: patterns.sv(13)sv_indent_004 -- Indent the line of the list by 16 spaces", lOutput)
        self.assertEqual([], only(self.run_mhsg(["-ap"], "patterns.fixed.sv")[1], "sv_indent"))

    def test_expanded_list_indent(self):
        # The arguments of a call and the constraints of a randomize with whose bracket ends its line are one level in,
        # two in the condition of an if, as Verible lays them out; arguments after the ( are left alone
        _, lOutput, sAfter = self.run_mhsg(["--fix"], "lists.sv")
        self.assertEqual(read("lists.fixed.sv"), sAfter)
        _, lOutput, _ = self.run_mhsg(["-ap"], "lists.sv")
        self.assertEqual(9, len([s for s in lOutput if ")sv_indent_004 " in s]))
        self.assertIn("ERROR: lists.sv(6)sv_indent_004 -- Indent the line of the list by 16 spaces", lOutput)
        self.assertEqual([], only(self.run_mhsg(["-ap"], "lists.fixed.sv")[1], "sv_indent"))

    def test_escaped_identifier_keeps_its_space(self):
        # An escaped identifier ends at whitespace: removing the space before the semicolon would change the code
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "escaped.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module escaped;\n    reg \\busa+index ;\n    reg \\-clock  ;\nendmodule\n")
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix"], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual("module escaped;\n    reg \\busa+index ;\n    reg \\-clock ;\nendmodule\n", oFile.read())

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
        # sv_syntax_001 reports code slang cannot parse; the rules on constructs check only the code before it. A
        # macro defined in another file is not an error.
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "e.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write("module e;\n    always @* y = a +;\n    `UNDEFINED(x)\nendmodule\n")
            oResult = subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "-of", "syntastic"], cwd=sRoot, capture_output=True, text=True, check=False)
        self.assertEqual([f"ERROR: {sCopy}(2)sv_syntax_001 -- Syntax error: expected expression"], oResult.stdout.splitlines())

    def test_code_before_a_syntax_error(self):
        # The code before the syntax error is checked and fixed, and so are the items of the module after the one with
        # the error; the item with the error is not, from the line of the error
        sText = "module e;\nlogic  x ;\n    always_comb begin\n    x=a;\n    end\n    assign y = a +;\n  logic   z ;\nendmodule\n"
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "e.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write(sText)
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sCopy, "-ap", "-of", "syntastic"],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix"], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                sAfter = oFile.read()
        self.assertEqual(
            [
                f"ERROR: {sCopy}(2)sv_indent_001 -- Use 4 spaces for indent",
                f"ERROR: {sCopy}(2)sv_whitespace_003 -- Remove space before semicolon",
                f"ERROR: {sCopy}(4)sv_indent_001 -- Use 8 spaces for indent",
                f"ERROR: {sCopy}(4)sv_whitespace_008 -- Add a space around the operator",
                f"ERROR: {sCopy}(4)sv_whitespace_008 -- Add a space around the operator",
                f"ERROR: {sCopy}(6)sv_syntax_001 -- Syntax error: expected expression",
                f"ERROR: {sCopy}(7)sv_indent_001 -- Use 4 spaces for indent",
                f"ERROR: {sCopy}(7)sv_whitespace_003 -- Remove space before semicolon",
            ],
            oResult.stdout.splitlines(),
        )
        self.assertEqual("module e;\n    logic  x;\n    always_comb begin\n        x = a;\n    end\n    assign y = a +;\n    logic   z;\nendmodule\n", sAfter)

    def test_units_after_a_syntax_error(self):
        # A syntax error leaves its item alone, from its line on; the other items and modules are checked
        sText = "module a;\nlogic x;\nendmodule\n\nmodule b;\n    logic y;\n    wire w = ;\n  logic v;\nendmodule\n\nmodule c;\nlogic z;\nendmodule\n"
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "u.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write(sText)
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sCopy, "-ap", "-of", "syntastic"],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(
            [
                f"ERROR: {sCopy}(2)sv_indent_001 -- Use 4 spaces for indent",
                f"ERROR: {sCopy}(7)sv_syntax_001 -- Syntax error: expected expression",
                f"ERROR: {sCopy}(8)sv_alignment_004 -- Align v in column 11",
                f"ERROR: {sCopy}(8)sv_indent_001 -- Use 4 spaces for indent",
                f"ERROR: {sCopy}(12)sv_indent_001 -- Use 4 spaces for indent",
            ],
            [s for s in oResult.stdout.splitlines() if "sv_comment" not in s and "sv_file" not in s],
        )

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

    def test_starc_checks(self):
        # One violation of each: the case default may assign x, and the asynchronous reset may use negedge
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more.sv")
        lRules = ("sv_naming_014", "sv_naming_015", "sv_always_007", "sv_statement_007", "sv_statement_009", "sv_dimension_003")
        lRules += ("sv_literal_006", "sv_module_003", "sv_declaration_002", "sv_comment_002")
        self.assertEqual(
            [
                "WARNING: starc_more.sv(4)STARC-3.1.5.3 (sv_declaration_002) -- Give Depth a default value",
                "WARNING: starc_more.sv(6)STARC-1.1.1.6 (sv_naming_014) -- Rename clk__i, which has two underscores in a row",
                "WARNING: starc_more.sv(8)STARC-2.1.6.2 (sv_dimension_003) -- Number the bits from 0",
                "WARNING: starc_more.sv(10)STARC-1.1.1.6 (sv_naming_014) -- Rename flag_, which ends with an underscore",
                "WARNING: starc_more.sv(12)STARC-3.5.6.7 (sv_comment_002) -- Use // comments",
                "WARNING: starc_more.sv(18)STARC-1.4.3.6 (sv_always_007) -- Clock the register on the rising edge",
                "ERROR: starc_more.sv(26)STARC-2.1.6.5/STARC-2.10.1.5/STARC-2.10.1.6 (sv_literal_006) -- Do not use x or z in a literal",
                "WARNING: starc_more.sv(26)STARC-2.1.5.1 (sv_statement_007) -- Do not nest the conditional operator",
                "ERROR: starc_more.sv(30)STARC-2.9.1.2 (sv_statement_009) -- Do not change the loop variable i in the loop",
                "ERROR: starc_more.sv(34)STARC-3.2.3.1 (sv_module_003) -- Connect the ports by name",
                "WARNING: starc_more.sv(34)STARC-1.1.1.8 (sv_naming_015) -- Name the instance sub, or sub_<number>",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )
        # The limits of the sizes, made small
        with tempfile.TemporaryDirectory() as sTemporary:
            sConfiguration = os.path.join(sTemporary, "small.yaml")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                oFile.write(
                    "rule:\n  sv_always_008:\n    maximum_outputs: 0\n  sv_always_009:\n    maximum_lines: 6\n"
                    "  sv_statement_008:\n    maximum_depth: 0\n  sv_case_004:\n    maximum_items: 1\n",
                )
            _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap", "-c", sConfiguration], "starc_more.sv")
        lRules = ("sv_always_008", "sv_always_009", "sv_statement_008", "sv_case_004")
        self.assertEqual(
            [
                "WARNING: starc_more.sv(18)STARC-2.6.1.3 (sv_always_008) -- Split the always block: it assigns 1 signal, more than 0",
                "WARNING: starc_more.sv(18)STARC-2.6.1.4 (sv_always_009) -- Split the always block: it has 7 lines, more than 6",
                "WARNING: starc_more.sv(19)STARC-2.7.3.1 (sv_statement_008) -- Nest if statements at most 0 deep",
                "WARNING: starc_more.sv(28)STARC-2.6.1.3 (sv_always_008) -- Split the always block: it assigns 1 signal, more than 0",
                "WARNING: starc_more.sv(38)STARC-2.6.1.3 (sv_always_008) -- Split the always block: it assigns 1 signal, more than 0",
                "WARNING: starc_more.sv(39)STARC-2.8.2.2 (sv_case_004) -- Split the case statement: it has 2 items, more than 1",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_2(self):
        # One violation of each; the reset tested by the first if is not a clock, and the case default may be anything
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more2.sv")
        lRules = ("sv_function_006", "sv_function_007", "sv_function_008", "sv_always_010", "sv_always_011", "sv_always_012")
        lRules += ("sv_always_013", "sv_always_014", "sv_statement_010", "sv_statement_011", "sv_statement_012", "sv_statement_013")
        lRules += ("sv_case_005", "sv_case_006", "sv_case_007", "sv_declaration_003")
        self.assertEqual(
            [
                "WARNING: starc_more2.sv(13)STARC-3.1.3.4 (sv_declaration_003) -- Declare one signal per declaration",
                "ERROR: starc_more2.sv(19)STARC-2.1.2.3 (sv_function_006) -- Pass b_i to add as arguments",
                "ERROR: starc_more2.sv(20)STARC-2.1.3.5 (sv_function_007) -- Do not assign valid in a function: return the value",
                "ERROR: starc_more2.sv(25)STARC-2.1.2.5 (sv_function_008) -- Do not wait for a clock edge in a task",
                "WARNING: starc_more2.sv(28)STARC-2.2.2.2 (sv_always_010) -- Remove the constant from the sensitivity list",
                "ERROR: starc_more2.sv(28)STARC-2.6.2.2 (sv_always_011) -- Remove r, which the block assigns, from its sensitivity list",
                "WARNING: starc_more2.sv(32)STARC-2.3.6.2 (sv_always_013) -- Make the asynchronous reset active low, with negedge",
                "ERROR: starc_more2.sv(32)STARC-1.3.1.7/STARC-2.3.1.7 (sv_always_014) -- Give the register at most one asynchronous reset or set",
                "ERROR: starc_more2.sv(40)STARC-2.3.3.1/STARC-2.3.3.2 (sv_always_012) -- Clock the always block on one edge of one clock",
                "WARNING: starc_more2.sv(45)STARC-2.10.1.2 (sv_statement_012) -- Parenthesize the mixed && and ||",
                "WARNING: starc_more2.sv(47)STARC-2.7.1.3 (sv_statement_010) -- End the if chain with an else",
                "WARNING: starc_more2.sv(47)STARC-2.10.7.1 (sv_statement_011) -- Compute the arithmetic outside the if condition",
                "ERROR: starc_more2.sv(50)STARC-2.10.8.1 (sv_statement_013) -- Divide signals, not expressions",
                "WARNING: starc_more2.sv(51)STARC-2.8.4.3 (sv_case_005) -- Use case instead of casez",
                "WARNING: starc_more2.sv(51)STARC-2.8.5.4 (sv_case_007) -- Compute the case selector in a signal of its own",
                "ERROR: starc_more2.sv(52)STARC-2.8.5.3 (sv_case_006) -- Use a constant as the case label, not ready",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_3(self):
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more3.sv")
        lRules = ("sv_file_005", "sv_naming_016", "sv_module_004", "sv_module_005", "sv_module_006", "sv_dimension_004")
        self.assertEqual(
            [
                "WARNING: starc_more3.sv(2)STARC-3.2.2.7 (sv_module_006) -- Use a parameter for the constant WIDTH",
                "WARNING: starc_more3.sv(3)STARC-1.1.4.1/STARC-3.5.2.5 (sv_file_005) -- Name the include file with one of the extensions .h, .vh, .svh, .inc",
                "WARNING: starc_more3.sv(5)STARC-1.1.2.5/STARC-1.1.3.1 (sv_naming_016) -- Name the port clk like a port, matching [a-z0-9_]+_n?(i|o|io)",
                "WARNING: starc_more3.sv(6)STARC-1.1.4.7/STARC-3.1.5.1/STARC-3.1.5.2 (sv_dimension_004) -- Write the width of the port with a parameter",
                "WARNING: starc_more3.sv(10)STARC-1.1.2.5/STARC-1.1.3.1 (sv_naming_016) -- Name the signal count_o unlike a port, not matching [a-z0-9_]+_n?(i|o|io)",
                "ERROR: starc_more3.sv(12)STARC-1.2.1.2 (sv_module_005) -- Use an expression instead of the and primitive",
                "WARNING: starc_more3.sv(13)STARC-1.1.4.6 (sv_module_004) -- Do not drive the output ready_o with a constant",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_4(self):
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more4.sv")
        lRules = (
            "sv_always_015",
            "sv_always_016",
            "sv_module_007",
            "sv_module_008",
            "sv_file_006",
            "sv_literal_007",
            "sv_literal_008",
            "sv_function_009",
            "sv_statement_014",
            "sv_comment_003",
        )
        self.assertEqual(
            [
                "WARNING: starc_more4.sv(1)STARC-3.5.3.1/STARC-3.5.3.3 (sv_comment_003) -- Start the file with a header comment",
                "WARNING: starc_more4.sv(2)STARC-3.2.2.5 (sv_module_008) -- Do not use the macro `WIDTH_M in the macro DEPTH_M",
                "WARNING: starc_more4.sv(3)STARC-4.1.2.4 (sv_file_006) -- Declare the time unit with `timescale or timeunit",
                "WARNING: starc_more4.sv(5)STARC-3.1.3.2 (sv_module_007) -- Move the clock port clk_i before the input ports",
                "WARNING: starc_more4.sv(7)STARC-3.1.3.2 (sv_module_007) -- Move the reset port rst_ni before the output ports",
                "WARNING: starc_more4.sv(8)STARC-3.1.3.2 (sv_module_007) -- Move the input port count_i before the output ports",
                "ERROR: starc_more4.sv(11)STARC-2.3.1.6 (sv_always_015) -- The reset rst_ni is tested low: use negedge",
                "WARNING: starc_more4.sv(18)STARC-2.3.6.1 (sv_always_016) -- Reset s too, or assign it in an always block without reset",
                "ERROR: starc_more4.sv(20)STARC-2.10.3.6 (sv_literal_007) -- Give the constant 3 a width",
                "WARNING: starc_more4.sv(21)STARC-2.10.3.5 (sv_literal_008) -- Write 5 with a base, such as 'd5",
                "WARNING: starc_more4.sv(22)STARC-2.1.3.4 (sv_function_009) -- End the function parity by assigning its result",
                "WARNING: starc_more4.sv(27)STARC-4.1.2.3 (sv_statement_014) -- Shorten the fork join block: it has 6 lines, more than 5",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_5(self):
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more5.sv")
        lRules = (
            "sv_naming_017",
            "sv_always_017",
            "sv_always_018",
            "sv_always_019",
            "sv_always_020",
            "sv_statement_015",
            "sv_statement_016",
            "sv_statement_017",
            "sv_statement_018",
            "sv_statement_019",
            "sv_statement_020",
            "sv_statement_021",
            "sv_statement_022",
            "sv_statement_023",
            "sv_statement_024",
            "sv_statement_025",
            "sv_function_010",
            "sv_file_007",
            "sv_comment_004",
            "sv_comment_005",
            "sv_case_008",
            "sv_case_009",
        )
        self.assertEqual(
            [
                "WARNING: starc_more5.sv(1)STARC-3.5.6.4/STARC-3.5.6.5 (sv_comment_005) -- Write the comment with ASCII characters only",
                "WARNING: starc_more5.sv(9)STARC-3.5.6.3 (sv_comment_004) -- Describe mem in a comment",
                "WARNING: starc_more5.sv(11)STARC-2.3.1.4 (sv_statement_016) -- Give delays only in always blocks",
                "WARNING: starc_more5.sv(11)STARC-2.5.1.2 (sv_statement_017) -- Use a plain signal as the enable of the tri-state buffer",
                "WARNING: starc_more5.sv(12)STARC-1.1.1.7 (sv_naming_017) -- Mark the active low reset rst_i with a suffix such as _n",
                "ERROR: starc_more5.sv(16)STARC-2.2.3.2/STARC-2.2.3.3 (sv_always_017) -- Assign q once: it is already assigned before in the block",
                "WARNING: starc_more5.sv(21)STARC-2.3.5.1/STARC-3.3.3.2 (sv_always_019) -- The register ready is always assigned the same constant: use the constant",
                "WARNING: starc_more5.sv(21)STARC-2.7.2.1 (sv_statement_019) -- Merge this branch with the one on line 20, which has the same statements",
                "ERROR: starc_more5.sv(23)STARC-2.9.2.4 (sv_always_020) -- Use one for loop in the reset branch and another in the other branch",
                "WARNING: starc_more5.sv(25)STARC-2.1.6.3 (sv_statement_023) -- Index with a signal, not the expression addr + 1",
                "WARNING: starc_more5.sv(27)STARC-2.5.1.7/STARC-2.5.1.8/STARC-2.5.1.9 (sv_statement_018) -- Do not test the tri-state signal bus",
                "WARNING: starc_more5.sv(28)STARC-2.7.2.1 (sv_statement_019) -- Merge this branch with the one on line 27, which has the same statements",
                "WARNING: starc_more5.sv(29)STARC-2.5.1.7/STARC-2.5.1.8/STARC-2.5.1.9 (sv_statement_018) -- Do not test the tri-state signal bus",
                "WARNING: starc_more5.sv(29)STARC-2.7.2.2 (sv_statement_020) -- Remove the branch: its condition repeats the one on line 27",
                "WARNING: starc_more5.sv(30)STARC-2.7.2.1 (sv_statement_019) -- Merge this branch with the one on line 29, which has the same statements",
                "WARNING: starc_more5.sv(31)STARC-2.10.1.3 (sv_statement_021) -- Add parentheses to s - r + q",
                "WARNING: starc_more5.sv(31)STARC-2.10.5.5 (sv_statement_022) -- Compute r + s outside the conditional operator",
                "WARNING: starc_more5.sv(31)STARC-2.10.5.5 (sv_statement_022) -- Compute s - r + q outside the conditional operator",
                "WARNING: starc_more5.sv(34)STARC-2.11.1.3/STARC-2.11.4.2 (sv_case_008) -- Name the state encoding 2'b00 with a parameter",
                "WARNING: starc_more5.sv(38)STARC-4.2.3.2 (sv_function_010) -- Do not give the task send the output done",
                "ERROR: starc_more5.sv(39)STARC-2.3.1.5 (sv_statement_015) -- Use a non-negative integer delay",
                "WARNING: starc_more5.sv(42)STARC-4.1.4.1/STARC-4.1.4.2 (sv_always_018) -- Assign r in one procedural block: another block assigns it too",
                "WARNING: starc_more5.sv(42)STARC-4.1.2.2 (sv_statement_024) -- Use a blocking assignment (=) in the initial block",
                "WARNING: starc_more5.sv(43)STARC-4.1.11.1 (sv_statement_025) -- Use $fstrobe instead of $fdisplay",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_6(self):
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more6.sv")
        lRules = (
            "sv_always_021",
            "sv_always_022",
            "sv_always_023",
            "sv_always_024",
            "sv_always_025",
            "sv_module_009",
            "sv_module_010",
            "sv_module_011",
            "sv_module_012",
            "sv_function_011",
            "sv_statement_026",
            "sv_statement_027",
            "sv_statement_028",
            "sv_statement_029",
            "sv_statement_030",
            "sv_statement_031",
            "sv_statement_032",
            "sv_statement_033",
            "sv_statement_034",
            "sv_case_010",
            "sv_literal_009",
        )
        self.assertEqual(
            [
                "WARNING: starc_more6.sv(10)STARC-1.3.2.1 (sv_always_023) -- Make the reset rst_n in a reset module, not with logic here",
                "WARNING: starc_more6.sv(12)STARC-1.3.1.2 (sv_always_021) -- Reset with rst_ni asynchronously",
                "WARNING: starc_more6.sv(12)STARC-2.1.4.2 (sv_statement_026) -- Use the bitwise operator instead of !",
                "ERROR: starc_more6.sv(15)STARC-2.1.2.1 (sv_always_024) -- Do not call init in the reset of the register",
                "WARNING: starc_more6.sv(15)STARC-2.1.4.2 (sv_statement_026) -- Use the bitwise operator instead of !",
                "ERROR: starc_more6.sv(16)STARC-1.4.3.4/STARC-3.3.3.1 (sv_always_022) -- Do not use the clock clk_i as data",
                "WARNING: starc_more6.sv(17)STARC-2.4.1.1/STARC-2.4.1.2 (sv_module_010) -- Put the latch in a module of its own",
                "WARNING: starc_more6.sv(18)STARC-2.4.1.3 (sv_always_025) -- Do not reset the latch with rst_ni",
                "WARNING: starc_more6.sv(18)STARC-2.1.4.2 (sv_statement_026) -- Use the bitwise operator instead of !",
                "WARNING: starc_more6.sv(20)STARC-2.5.1.1 (sv_module_011) -- Put the tri-state buffer in a module of its own",
                "WARNING: starc_more6.sv(21)STARC-3.1.2.2 (sv_module_012) -- Keep the vendor primitive BUFG out of the technology independent code",
                "WARNING: starc_more6.sv(24)STARC-2.1.4.2 (sv_statement_026) -- Use the bitwise operator instead of &&",
                "WARNING: starc_more6.sv(24)STARC-2.1.4.2 (sv_statement_026) -- Use the bitwise operator instead of !",
                "WARNING: starc_more6.sv(25)STARC-2.8.3.4/STARC-2.8.3.6/STARC-2.8.3.7 (sv_statement_028) -- Do not test sel, which may be assigned x",
                "WARNING: starc_more6.sv(28)STARC-2.7.3.4 (sv_statement_027) -- Merge the condition of this if with the one of the if around it",
                "ERROR: starc_more6.sv(29)STARC-2.9.2.1/STARC-2.9.2.2 (sv_statement_029) -- Compute a_i + q outside the loop",
                "ERROR: starc_more6.sv(30)STARC-2.10.4.5/STARC-2.10.4.6 (sv_literal_009) -- Do not assign the negative value -1",
                "WARNING: starc_more6.sv(33)STARC-2.11.2.1 (sv_case_010) -- Put the state machine of mode_state in a module of its own",
                "ERROR: starc_more6.sv(35)STARC-2.1.1.2 (sv_function_011) -- Add an else to the if of the function",
                "WARNING: starc_more6.sv(37)STARC-4.3.11.3 (sv_statement_033) -- Put $display between translate_off and translate_on pragmas",
                "WARNING: starc_more6.sv(42)STARC-4.1.6.1 (sv_statement_030) -- Compute the delay once, as a parameter",
                "WARNING: starc_more6.sv(44)STARC-4.1.1.2 (sv_statement_034) -- Give the delay 5 with a parameter",
                "WARNING: starc_more6.sv(45)STARC-4.1.7.1 (sv_statement_031) -- Generate the clock clk_b in a block of its own",
                "WARNING: starc_more6.sv(45)STARC-4.1.1.2 (sv_statement_034) -- Give the delay 5 with a parameter",
                "WARNING: starc_more6.sv(46)STARC-4.1.8.4 (sv_statement_032) -- Wait for done on a clock edge, not on its own edge",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_do254_checks(self):
        # The DO-254 checks of SystemVerilog files: the rules that map to them for VHDL files, written for SystemVerilog
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254_plus", "--lint_only", "-ap"], "do254.sv")
        lRules = (
            "sv_always_027",
            "sv_always_028",
            "sv_always_029",
            "sv_comment_008",
            "sv_declaration_004",
            "sv_statement_051",
            "sv_literal_010",
            "sv_comment_007",
        )
        self.assertEqual(
            [
                "WARNING: do254.sv(5)DO254-DR11 (sv_comment_007) -- Comment the module more: 6 of its 45 lines have a comment",
                "ERROR: do254.sv(10)DO254-SS16 (sv_declaration_004) -- Remove the initial value of q_o, and reset it instead",
                "ERROR: do254.sv(15)DO254-SS16 (sv_declaration_004) -- Remove the initial value of busy, and reset it instead",
                "WARNING: do254.sv(23)DO254-SS1 (sv_statement_051) -- a_d inverts a_n, which inverts a signal too: remove the chain of inverters",
                "WARNING: do254.sv(26)DO254-DR1 (sv_always_029) -- Label the always block, with begin : name",
                "WARNING: do254.sv(27)DO254-SS14 (sv_always_027) -- The register busy has no reset: give it a reset, or justify it without one",
                "WARNING: do254.sv(34)DO254-CP3 (sv_literal_010) -- Name 4'd5 with a parameter",
                "WARNING: do254.sv(39)DO254-SS13 (sv_always_028) -- Use rst_ni as on line 32, active low and asynchronous, not active high and synchronous",
                "WARNING: do254.sv(43)DO254PLUS-DEAD (sv_comment_008) -- Remove commented-out code",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )
        # The same code written to pass: the memory needs no reset, and the comments describe it
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254_plus", "--lint_only", "-ap"], "do254_clean.sv")
        self.assertEqual([], [s for s in lOutput if any(f"({r})" in s for r in lRules)])
        # SS20 limits the nesting to four levels, which sv_statement_008 is set to under do254
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254", "--lint_only", "-ap"], "do254_nesting.sv")
        self.assertEqual(
            ["WARNING: do254_nesting.sv(17)DO254-SS20 (sv_statement_008) -- Nest if statements at most 4 deep"],
            [s for s in lOutput if "(sv_statement_008)" in s],
        )

    def test_do254_numbers(self):
        # CP3, as lint_034 for VHDL: the numbers in the statements of every case item, default included, and in
        # ordinary statements; not the values of the case items, nor the parameter values given to an instance
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254", "--lint_only", "-ap"], "do254_numbers.sv")
        self.assertEqual(
            [
                "WARNING: do254_numbers.sv(18)DO254-CP3 (sv_literal_010) -- Name 8'h0d with a parameter",
                "WARNING: do254_numbers.sv(19)DO254-CP3 (sv_literal_010) -- Name 8'h0a with a parameter",
                "WARNING: do254_numbers.sv(24)DO254-CP3 (sv_literal_010) -- Name 8'd3 with a parameter",
            ],
            [s for s in lOutput if "(sv_literal_010)" in s],
        )

    def test_do254_checks_more(self):
        # The DO-254 checks of SystemVerilog files that follow paths through the code, instances, states and comments;
        # sv_module_018 does not check the instances of leaf, which is instantiated twice, see names_across_hierarchy.sv
        # do254_more.sv is checked on its own, so its top module do254_more is not known as a top level and its inout
        # port pad_io is reported, see test_inout_ports_of_the_top_level
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254_plus", "--lint_only", "-ap"], "do254_more.sv")
        lRules = (
            "sv_always_030",
            "sv_always_031",
            "sv_always_032",
            "sv_case_013",
            "sv_comment_009",
            "sv_comment_010",
            "sv_declaration_005",
            "sv_lint_017",
            "sv_lint_018",
            "sv_module_018",
            "sv_module_019",
            "sv_module_020",
            "sv_statement_052",
        )
        self.assertEqual(
            [
                "WARNING: do254_more.sv(8)DO254PLUS-REQ (sv_comment_010) -- Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the module",
                "WARNING: do254_more.sv(9)DO254PLUS-GENERIC (sv_module_019) -- Check the parameters of leaf with an assertion",
                "WARNING: do254_more.sv(20)DO254PLUS-REQ (sv_comment_010) -- Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the module",
                "WARNING: do254_more.sv(25)DO254PLUS-PORT (sv_module_020) -- Use inout ports only on the top level, for device pins",
                "WARNING: do254_more.sv(40)DO254-CP12 (sv_lint_018) -- Output port 'valid_o' is explicitly connected to nothing",
                "ERROR: do254_more.sv(43)DO254-CP11 (sv_lint_017) -- Input port 'data_i' has no connection",
                "ERROR: do254_more.sv(49)DO254-SS3 (sv_statement_052) -- hold is assigned from itself, a combinational loop",
                "WARNING: do254_more.sv(52)DO254PLUS-PRAGMA (sv_comment_009) -- Code from here is hidden from synthesis; justify the region",
                "WARNING: do254_more.sv(56)DO254PLUS-REQ (sv_comment_010) -- Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the always block",
                "ERROR: do254_more.sv(57)DO254-CP6 (sv_case_013) -- State Fault of state_q is never assigned, so the machine never enters it",
                "WARNING: do254_more.sv(58)DO254PLUS-DEFAULT (sv_always_032) -- Give state_d a default value at the start of the block",
                "ERROR: do254_more.sv(60)DO254-CP6 (sv_case_013) -- State Done of state_q assigns no other state, so the machine never leaves it",
                "WARNING: do254_more.sv(65)DO254PLUS-REQ (sv_comment_010) -- Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the always block",
                "ERROR: do254_more.sv(66)DO254-DR3 (sv_declaration_005) -- Rename count: the module declares a signal count too",
                "WARNING: do254_more.sv(68)DO254PLUS-DEFAULT (sv_always_032) -- Give sum a default value at the start of the block",
                "ERROR: do254_more.sv(69)DO254-CP10/DO254-SS3 (sv_always_030) -- Assign sum on every path before reading it: the block reads the value of its last run",
                "WARNING: do254_more.sv(76)DO254PLUS-REQ (sv_comment_010) -- Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the always block",
                "WARNING: do254_more.sv(78)DO254-CP10/DO254PLUS-VAR (sv_always_031) -- acc keeps its value from the previous clock edge, a hidden register: assign it before reading it, or use a nonblocking assignment",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )
        # The same design written to pass: defaults, tags, an assertion and every state entered and left
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254_plus", "--lint_only", "-ap"], "do254_more_clean.sv")
        self.assertEqual([], [s for s in lOutput if any(f"({r})" in s for r in lRules)])

    def test_names_across_hierarchy(self):
        # sv_module_018 (DR9) compares names without the suffixes of ports named by direction, _n_i and _ni too, and
        # skips the ports of a module instantiated more than once, or in a loop generate; data_i (foo) is a rename
        _, lOutput, _ = self.run_mhsg(["--rule_set", "do254", "--lint_only"], "names_across_hierarchy.sv")
        self.assertEqual(
            ["WARNING: names_across_hierarchy.sv(44)DO254-DR9 (sv_module_018) -- Signal foo connected to port data_i of u_leaf has another name"],
            [s for s in lOutput if "(sv_module_018)" in s],
        )

    def test_sensitivity_list_branches(self):
        # t is written in both branches before it is read; u only in one, so its old value is read
        _, lOutput, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], "sensitivity_branches.sv")
        self.assertEqual(
            ["ERROR: sensitivity_branches.sv(21)sv_lint_008 -- Add c_i, u to the sensitivity list, or use always_comb"],
            [s for s in lOutput if "sv_lint_008" in s],
        )

    def test_starc_checks_7(self):
        # The widths come from slang's elaboration of the file
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more7.sv")
        lRules = (
            "sv_statement_035",
            "sv_statement_036",
            "sv_statement_037",
            "sv_statement_038",
            "sv_statement_039",
            "sv_statement_040",
            "sv_statement_041",
            "sv_statement_042",
            "sv_statement_043",
        )
        self.assertEqual(
            [
                "WARNING: starc_more7.sv(16)STARC-2.1.4.5 (sv_statement_035) -- Compare a_i, 8 bits wide, with a value instead of using it as a truth value",
                "WARNING: starc_more7.sv(17)STARC-2.1.5.3 (sv_statement_036) -- Make the condition c_i 1 bit wide: it has 6 bits",
                "WARNING: starc_more7.sv(18)STARC-2.10.3.1 (sv_statement_037) -- Compare operands of the same width: a_i has 8 bits, c_i 6",
                "WARNING: starc_more7.sv(19)STARC-2.10.4.4 (sv_statement_043) -- Compare values of one type: i == a_i compares integer with logic[7:0]",
                "WARNING: starc_more7.sv(20)STARC-2.10.3.4 (sv_statement_038) -- Extend c_i, 6 bits wide, to the 8 bits of y_o",
                "WARNING: starc_more7.sv(21)STARC-2.10.6.1 (sv_statement_039) -- Make sum 9 bits wide to hold the result of a_i + b_i",
                "WARNING: starc_more7.sv(23)STARC-2.1.4.6 (sv_statement_042) -- The reduction &a_i gives 1 bit, here extended to 4",
                "WARNING: starc_more7.sv(23)STARC-2.1.4.6 (sv_statement_042) -- The reduction &b_i gives 1 bit, here extended to 4",
                "ERROR: starc_more7.sv(24)STARC-2.10.8.2/STARC-2.10.8.3 (sv_statement_040) -- Divide at most 12 bits: d_i has 16",
                "ERROR: starc_more7.sv(24)STARC-2.10.8.2/STARC-2.10.8.3 (sv_statement_040) -- Divide by at most 8 bits: e_i[9:0] has 10",
                "ERROR: starc_more7.sv(25)STARC-2.10.8.2/STARC-2.10.8.3 (sv_statement_040) -- Divide at most 12 bits: d_i has 16",
                "WARNING: starc_more7.sv(26)STARC-2.10.6.1 (sv_statement_039) -- Make p_o 64 bits wide to hold the result of e_i * e_i",
                "WARNING: starc_more7.sv(26)STARC-2.10.6.5 (sv_statement_041) -- Build the multiplier of e_i * e_i explicitly: its operands have up to 32 bits",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
        )

    def test_starc_checks_8(self):
        _, lOutput, _ = self.run_mhsg(["--rule_set", "starc", "-ap"], "starc_more8.sv")
        lRules = (
            "sv_naming_018",
            "sv_naming_019",
            "sv_naming_020",
            "sv_module_013",
            "sv_module_014",
            "sv_module_015",
            "sv_module_016",
            "sv_module_017",
            "sv_always_026",
            "sv_case_011",
            "sv_case_012",
            "sv_statement_044",
            "sv_statement_045",
            "sv_statement_046",
            "sv_statement_047",
            "sv_statement_048",
            "sv_statement_049",
            "sv_statement_050",
            "sv_literal_010",
            "sv_comment_006",
            "sv_comment_007",
        )
        self.assertEqual(
            [
                "WARNING: starc_more8.sv(1)STARC-3.5.3.2 (sv_comment_006) -- Record the changes in the file header: modif|change|history|revision",
                "WARNING: starc_more8.sv(5)STARC-3.5.6.1 (sv_comment_007) -- Comment the module more: 1 of its 35 lines have a comment",
                "WARNING: starc_more8.sv(12)STARC-1.1.1.9 (sv_naming_018) -- Rename Y_O, which differs from y_o only in case",
                "WARNING: starc_more8.sv(14)STARC-1.1.4.4 (sv_module_013) -- Undefine LOCAL with an undef directive before the end of the module",
                "ERROR: starc_more8.sv(18)STARC-1.6.4.1 (sv_module_015) -- Move the logic to a basic block: this module connects instances",
                "WARNING: starc_more8.sv(18)STARC-1.1.5.2 (sv_naming_020) -- Name the clock sample with a clock word, such as clk",
                "WARNING: starc_more8.sv(18)STARC-1.1.5.2 (sv_naming_020) -- Name the reset init_n with a reset word, such as rst",
                "WARNING: starc_more8.sv(19)STARC-2.3.1.3 (sv_always_026) -- Add a unit delay to the register assignment, as in <= #1",
                "WARNING: starc_more8.sv(20)STARC-2.3.1.3 (sv_always_026) -- Add a unit delay to the register assignment, as in <= #1",
                "WARNING: starc_more8.sv(21)STARC-1.3.1.4 (sv_module_014) -- Put the registers with a synchronous reset in a module of their own",
                "WARNING: starc_more8.sv(22)STARC-2.3.1.3 (sv_always_026) -- Add a unit delay to the register assignment, as in <= #1",
                "WARNING: starc_more8.sv(23)STARC-2.3.1.3 (sv_always_026) -- Add a unit delay to the register assignment, as in <= #1",
                "WARNING: starc_more8.sv(24)STARC-3.1.3.1 (sv_module_016) -- Connect a in the order of the ports of sub",
                "WARNING: starc_more8.sv(25)STARC-1.6.2.1 (sv_module_017) -- Register the output y_o",
                "WARNING: starc_more8.sv(29)STARC-2.9.1.1 (sv_statement_044) -- The loop makes priority logic for grant: write it as such",
                "WARNING: starc_more8.sv(30)STARC-2.9.2.3 (sv_statement_045) -- Run the loop at most 10 times: it runs 12",
                "WARNING: starc_more8.sv(31)STARC-3.2.2.1/STARC-4.1.2.1 (sv_literal_010) -- Name 8'd5 with a parameter",
                "WARNING: starc_more8.sv(31)STARC-2.9.1.1 (sv_statement_044) -- The loop makes priority logic for t: write it as such",
                "WARNING: starc_more8.sv(31)STARC-2.10.6.3 (sv_statement_046) -- Do not mix signed and unsigned operands in s + a_i",
                "WARNING: starc_more8.sv(33)STARC-2.8.4.4 (sv_case_012) -- Keep the wildcard bits of 4'b1?0? together",
                "WARNING: starc_more8.sv(33)STARC-2.10.6.6 (sv_statement_047) -- Write one arithmetic operation per line: this one has 2",
                "WARNING: starc_more8.sv(37)STARC-2.6.1.2 (sv_statement_050) -- Compute q & r once, in a signal: it is written 3 times",
                "ERROR: starc_more8.sv(52)STARC-4.1.3.1/STARC-4.1.3.2 (sv_statement_049) -- Offset the stimulus from the clock edge with a delay",
            ],
            [s for s in lOutput if any(f"({r})" in s for r in lRules)],
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
                "ERROR: top.sv(11)sv_lint_018 -- Output port 'unused_o' has no connection",
                "ERROR: top.sv(13)sv_lint_001 -- Implicit conversion of port connection truncates from 8 to 4 bits",
                "ERROR: top.sv(18)sv_lint_005 -- Unused variable 'extra'",
                "ERROR: sub.sv(5)sv_lint_010 -- Undriven output port 'unused_o'",
            ],
            self.run_project(["top.sv", "sub.sv"], ["--lint_only", "--rule_set", "none"]),
        )

    def test_state_machines_typed_in_a_package(self):
        # sv_case_013 finds the enum types of the other files of the run, by the bare name a module imports or the
        # name qualified with the package, and the states written either way
        lArguments = ["--lint_only", "--rule_set", "do254"]
        self.assertEqual(
            [
                "ERROR: fsm_user.sv(14)DO254-CP6 (sv_case_013) -- State Fault of state_q is never assigned, so the machine never enters it",
                "ERROR: fsm_user.sv(17)DO254-CP6 (sv_case_013) -- State Done of state_q assigns no other state, so the machine never leaves it",
                "ERROR: fsm_user.sv(38)DO254-CP6 (sv_case_013) -- State Done of state_q is never assigned, so the machine never enters it",
            ],
            [s for s in self.run_project(["fsm_user.sv", "fsm_pkg.sv"], lArguments) if "(sv_case_013)" in s],
        )
        # Without the package in the run the types are unknown, and the machines are not checked
        self.assertEqual([], [s for s in self.run_project(["fsm_user.sv"], lArguments) if "(sv_case_013)" in s])

    def test_inout_ports_of_the_top_level(self):
        # sv_module_020 leaves out the top level, a module no file of the run instantiates: its inout ports are the
        # pins of the device
        lArguments = ["--lint_only", "--rule_set", "do254_plus"]
        sSub = "WARNING: io_sub.sv(4)DO254PLUS-PORT (sv_module_020) -- Use inout ports only on the top level, for device pins"
        sTop = "WARNING: io_top.sv(4)DO254PLUS-PORT (sv_module_020) -- Use inout ports only on the top level, for device pins"
        self.assertEqual([sSub], [s for s in self.run_project(["io_top.sv", "io_sub.sv"], lArguments) if "(sv_module_020)" in s])
        # A file checked on its own does not show the design: its modules are not top levels, the top as the submodule
        self.assertEqual([sSub], [s for s in self.run_project(["io_sub.sv"], lArguments) if "(sv_module_020)" in s])
        self.assertEqual([sTop], [s for s in self.run_project(["io_top.sv"], lArguments) if "(sv_module_020)" in s])
        # Index files show it: the top is left out when they instantiate nothing of it, the submodule reported when they
        # instantiate it
        lIndexTop = ["--index_files", os.path.join(sDirectory, "project", "io_top.sv")]
        self.assertEqual([sSub], [s for s in self.run_project(["io_sub.sv"], lArguments + lIndexTop) if "(sv_module_020)" in s])
        lIndexSub = ["--index_files", os.path.join(sDirectory, "project", "io_sub.sv")]
        self.assertEqual([], [s for s in self.run_project(["io_top.sv"], lArguments + lIndexSub) if "(sv_module_020)" in s])
        # So does the design section, for a file on its own
        lDesign = ["-c", os.path.join(sDirectory, "project", "design.yaml")]
        self.assertEqual([], [s for s in self.run_project(["io_top.sv"], lArguments + lDesign) if "(sv_module_020)" in s])
        # A testbench in the run instantiates the top level, unless the design section names the top
        lFiles = ["io_tb.sv", "io_top.sv", "io_sub.sv"]
        self.assertEqual([sTop, sSub], [s for s in self.run_project(lFiles, lArguments) if "(sv_module_020)" in s])
        self.assertEqual([sSub], [s for s in self.run_project(lFiles, lArguments + lDesign) if "(sv_module_020)" in s])
        # Outside lint mode the run is not known, and every inout port is reported
        with tempfile.TemporaryDirectory() as sTemporary:
            sConfiguration = os.path.join(sTemporary, "c.yaml")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                oFile.write("rule:\n  sv_module_020:\n    disable: false\n")
            lOutput = self.run_project(["io_top.sv", "io_sub.sv"], ["-c", sConfiguration])
        self.assertEqual(
            [
                "ERROR: io_top.sv(4)sv_module_020 -- Use inout ports only on the top level, for device pins",
                "ERROR: io_sub.sv(4)sv_module_020 -- Use inout ports only on the top level, for device pins",
            ],
            [s for s in lOutput if "sv_module_020" in s],
        )

    def test_names_across_hierarchy_of_the_run(self):
        # sv_module_018 counts the instances of all the files of the run: hier_a.sv and hier_b.sv each instantiate
        # hier_sync once, so together their connections are not checked, and alone those of hier_a.sv are
        lArguments = ["--lint_only", "--rule_set", "do254"]
        self.assertEqual([], [s for s in self.run_project(["hier_a.sv", "hier_b.sv", "hier_sync.sv"], lArguments) if "(sv_module_018)" in s])
        self.assertEqual(
            [
                "WARNING: hier_a.sv(9)DO254-DR9 (sv_module_018) -- Signal a_i connected to port d_i of u_sync has another name",
                "WARNING: hier_a.sv(10)DO254-DR9 (sv_module_018) -- Signal a_o connected to port q_o of u_sync has another name",
            ],
            [s for s in self.run_project(["hier_a.sv", "hier_sync.sv"], lArguments) if "(sv_module_018)" in s],
        )

    def test_parameters_of_the_run(self):
        # sv_lint_014 and sv_lint_015 check the parameters of the modules of the run against each other, sv_lint_016
        # the macros one file defines and another uses
        lOutput = self.run_project(["params_sub.sv", "params_top.sv"], ["--lint_only", "--rule_set", "none"])
        self.assertEqual(
            [
                "ERROR: params_sub.sv(2)sv_lint_016 -- Macro PARAMS_DEPTH is used in params_top.sv but defined in the file of params_sub: define it in a file of global parameters",
                "ERROR: params_top.sv(3)sv_lint_015 -- Parameter WIDTH is also declared in module params_sub",
                "ERROR: params_top.sv(7)sv_lint_014 -- Instance of params_sub sets 1 of its 2 parameters; also set DEPTH",
            ],
            [s for s in lOutput if "sv_lint_01" in s],
        )

    def test_lint_of_inactive_code_and_macro_arguments(self):
        # The code of the inactive branch is linted with WIDE defined, and the warning in the code a macro argument
        # expands to is reported at the argument
        _, lOutput, _ = self.run_mhsg(["--lint_only", "--rule_set", "none"], "lint_unparsed.sv")
        self.assertEqual(
            [
                "ERROR: lint_unparsed.sv(9)sv_lint_001 -- Implicit conversion truncates from 8 to 4 bits",
                "ERROR: lint_unparsed.sv(13)sv_lint_001 -- Implicit conversion truncates from 8 to 4 bits",
            ],
            only(lOutput, "sv_lint"),
        )

    def test_whole_lines_of_inactive_code(self):
        # Every token of a line of an inactive branch is classified and checked, not only the first
        lTokens = tokens_of("module m;\n`ifdef X\n    assign y = a&b;\n`endif\nendmodule\n")
        oAnd = [o for o in lTokens if o.get_value() == "&"][0]
        self.assertTrue(oAnd.inactive)
        self.assertIsInstance(oAnd, tokens.of("BinaryAndExpression", "operatorToken"))

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
                "ERROR: alignment.sv(9)sv_alignment_011 -- Use 1 space(s) after [ to align the dimension",
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
