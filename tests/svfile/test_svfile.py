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
        sText = "module m;\n  logic a;  // trailing\n            // continued\nendmodule\n"
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "c.sv")
            with open(sCopy, "w", encoding="utf-8") as oFile:
                oFile.write(sText)
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix"], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual("module m;\n    logic a;  // trailing\n              // continued\nendmodule\n", oFile.read())

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
                oFile.write("module m;\nendmodule\n\n\n")
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
                oFile.write("module m;\n    always_comb begin\n        a = 1; b = 2;\n    end\nendmodule\n")
            sConfigurationFile = os.path.join(sTemporary, "c.yaml")
            with open(sConfigurationFile, "w", encoding="utf-8") as oFile:
                oFile.write("rule:\n  sv_statement_003:\n    disable: false\n")
            subprocess.run([sys.executable, "bin/mhsg", "-f", sCopy, "--fix", "-c", sConfigurationFile], cwd=sRoot, capture_output=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                self.assertEqual("module m;\n    always_comb begin\n        a = 1;\n        b = 2;\n    end\nendmodule\n", oFile.read())

    def test_sample_is_clean(self):
        self.assertEqual((0, []), self.run_mhsg([], "sample.sv")[:2])
