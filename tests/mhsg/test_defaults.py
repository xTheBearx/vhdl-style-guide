# -*- coding: utf-8 -*-
"""
The defaults: indent levels of 4 spaces and lines of 80 characters. Unlike the other tests, these run without the
settings the test files were written for, see tests/conftest.py and tests/test_defaults.yaml.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import pytest

from mhsg import rule
from mhsg.rules import block_comment, length, process

sDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults")
sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(lArguments):
    """Runs mhsg without tests/test_defaults.yaml and returns (exit status, output lines)."""
    oResult = subprocess.run([sys.executable, "bin/mhsg", *lArguments], cwd=sRoot, capture_output=True, text=True, check=False)
    return oResult.returncode, oResult.stdout.splitlines()


@pytest.mark.current_defaults
class test_defaults(unittest.TestCase):
    def test_rule_defaults(self):
        self.assertEqual(4, rule.DEFAULT_INDENT_SIZE)
        self.assertEqual(4, process.rule_016().indent_size)
        self.assertEqual(80, length.rule_001().length)
        self.assertEqual(80, block_comment.rule_001().max_header_column)
        self.assertEqual(80, block_comment.rule_003().max_footer_column)

    def test_four_spaces_pass(self):
        self.assertEqual((0, []), run(["-f", os.path.join(sDirectory, "four_spaces.vhd"), "-of", "syntastic"]))

    def test_two_spaces_fail(self):
        iStatus, lOutput = run(["-f", os.path.join(sDirectory, "two_spaces.vhd"), "-of", "syntastic"])
        self.assertEqual(1, iStatus)
        self.assertIn(f"ERROR: {os.path.join(sDirectory, 'two_spaces.vhd')}(7)port_004 -- Use 8 spaces for indent", lOutput)

    def test_long_line_fails(self):
        iStatus, lOutput = run(["-f", os.path.join(sDirectory, "long_line.vhd"), "-of", "syntastic"])
        # length_001 is a warning, which does not fail the run
        self.assertEqual(0, iStatus)
        self.assertEqual([f"WARNING: {os.path.join(sDirectory, 'long_line.vhd')}(21)length_001 -- Reduce line to less than 80 characters"], lOutput)

    def test_reindent_multiline_constraint_once(self):
        # Re-indenting moves the continuation lines of a multiline constraint, and with them its :=, so the :=
        # of the declarations are aligned after them (signal_400 before declarative_part_400): one fix is enough
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "multiline_constraint.vhd")
            shutil.copy(os.path.join(sDirectory, "multiline_constraint.vhd"), sCopy)
            lFixed = []
            for _ in range(2):
                run(["-f", sCopy, "--fix"])
                with open(sCopy, encoding="utf-8") as oFile:
                    lFixed.append(oFile.read())
            self.assertEqual(lFixed[0], lFixed[1])
            lLines = lFixed[0].splitlines()
            self.assertEqual(lLines[5].index(":="), lLines[6].index(":="))

    def test_styles_keep_two_spaces(self):
        with tempfile.TemporaryDirectory() as sTemporary:
            for sStyle, iLength in (("jcl", 120), ("indent_only", 80)):
                sConfiguration = os.path.join(sTemporary, sStyle + ".json")
                run(["--style", sStyle, "-oc", sConfiguration])
                with open(sConfiguration, encoding="utf-8") as oFile:
                    dRules = json.load(oFile)["rule"]
                with self.subTest(sStyle):
                    self.assertEqual(2, dRules["process_016"]["indent_size"])
                    self.assertEqual(iLength, dRules["length_001"]["length"])
