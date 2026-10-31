# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import if_statement
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_009_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_009_test_input.fixed.vhd"), lExpected)


lFile_then_and_nesting, eError_then_and_nesting = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_009_test_input.then_and_nesting.vhd"),
)

lExpected_then_and_nesting = []
lExpected_then_and_nesting.append("")
utils.read_file(os.path.join(sTestDir, "rule_009_test_input.then_and_nesting.fixed.vhd"), lExpected_then_and_nesting)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_009(self):
        oRule = if_statement.rule_009()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "if")
        self.assertEqual(oRule.identifier, "009")

        lExpected = [25, 26, 29, 30, 39, 50]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_009(self):
        oRule = if_statement.rule_009()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_009_then_and_nesting(self):
        # Issue VSG 1581: a then on its own line was aligned as a condition line, and parentheses nested three deep
        # were expected one column too far right.
        self.assertIsNone(eError_then_and_nesting)
        oRule = if_statement.rule_009()
        oFile = vhdlFile.vhdlFile(lFile_then_and_nesting)

        oRule.analyze(oFile)
        self.assertEqual([11, 15], utils.extract_violation_lines_from_violation_object(oRule.violations))

        oRule = if_statement.rule_009()
        oRule.fix(oFile)
        self.assertEqual(lExpected_then_and_nesting, oFile.get_lines())
