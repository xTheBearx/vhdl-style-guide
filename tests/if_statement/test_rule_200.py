# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import if_statement
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_200_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_200_test_input.fixed_no_blank.vhd"), lExpected)

lExpected_require_blank = []
lExpected_require_blank.append("")
utils.read_file(os.path.join(sTestDir, "rule_200_test_input.fixed_require_blank.vhd"), lExpected_require_blank)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_200(self):
        oRule = if_statement.rule_200()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "if")
        self.assertEqual(oRule.identifier, "200")

        lExpected = [26, 32, 52]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_200(self):
        oRule = if_statement.rule_200()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_200_w_require_blank(self):
        oRule = if_statement.rule_200()
        oRule.style = "require_blank_line"

        lExpected = [10, 12, 15, 17, 28, 36]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_200_w_require_blank(self):
        oRule = if_statement.rule_200()
        oRule.style = "require_blank_line"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_require_blank, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])
