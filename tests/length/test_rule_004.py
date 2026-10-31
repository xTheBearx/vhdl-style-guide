# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import length
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_004_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_004_default(self):
        oRule = length.rule_004()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "length")
        self.assertEqual(oRule.identifier, "004")
        self.assertTrue(oRule.disable)
        self.assertEqual(oRule.severity.name, "Error")

        lExpected = [3, 7, 9]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_004_with_125_characters(self):
        oRule = length.rule_004()
        oRule.length = 125

        lExpected = [3, 9]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

        oViolation = oRule.violations[0]
        self.assertEqual("Reduce line to less than 125 characters", oViolation.sSolution)
