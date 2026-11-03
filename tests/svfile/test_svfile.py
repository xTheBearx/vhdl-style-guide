# -*- coding: utf-8 -*-
"""
SystemVerilog files: tokens from slang, kept exactly as written, and the language neutral rules on them.
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from mhsg import language, parser, rule_list
from mhsg.svFile import svFile, tokens
from mhsg.vhdlFile import vhdlFile
from tests import utils

sDirectory = os.path.dirname(os.path.abspath(__file__))
sRoot = os.path.dirname(os.path.dirname(sDirectory))


def read(sName):
    with open(os.path.join(sDirectory, sName), encoding="utf-8") as oFile:
        return oFile.read()


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

    def test_only_language_neutral_rules(self):
        oRules = rule_list.rule_list(svFile(["module m;\n", "endmodule\n"], sFilename="m.sv"), None)
        self.assertEqual(["length_001", "length_002", "length_004", "whitespace_001", "whitespace_002"], sorted(o.unique_id for o in oRules.rules))
        self.assertTrue(all(language.SYSTEMVERILOG in o.languages for o in oRules.rules))
        self.assertGreater(len(rule_list.rule_list(vhdlFile([""]), None).rules), 1000)


class test_rules(unittest.TestCase):
    def run_mhsg(self, lArguments, sFile):
        """Runs mhsg on a copy of a test file; returns (exit status, output lines, file after)."""
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, sFile)
            shutil.copy(os.path.join(sDirectory, sFile), sCopy)
            oResult = subprocess.run([*utils.mhsg_exec(), "-f", sCopy, "-of", "syntastic", *lArguments], cwd=sRoot, capture_output=True, text=True, check=False)
            with open(sCopy, encoding="utf-8") as oFile:
                sAfter = oFile.read()
        return oResult.returncode, [s.replace(sCopy, sFile) for s in oResult.stdout.splitlines()], sAfter

    def test_check(self):
        # The leading tab of line 2 is left to the indentation rules, which SystemVerilog does not have yet;
        # the trailing whitespace of line 5 is inside an mhsg_off region
        iStatus, lOutput, _ = self.run_mhsg(["-ap", "-c", os.path.join(sDirectory, "length_80.yaml")], "style.sv")
        self.assertEqual(1, iStatus)
        self.assertEqual(
            [
                "ERROR: style.sv(2)whitespace_001 -- Remove trailing whitespace",
                "ERROR: style.sv(3)whitespace_002 -- Remove tab",
                "WARNING: style.sv(7)length_001 -- Reduce line to less than 80 characters",
            ],
            sorted(lOutput),
        )

    def test_fix(self):
        _, lOutput, sAfter = self.run_mhsg(["--fix", "-c", os.path.join(sDirectory, "length_80.yaml")], "style.sv")
        self.assertEqual(read("style.fixed.sv"), sAfter)
        self.assertEqual(["WARNING: style.sv(7)length_001 -- Reduce line to less than 80 characters"], lOutput)

    def test_sample_is_clean(self):
        self.assertEqual((0, []), self.run_mhsg([], "sample.sv")[:2])
