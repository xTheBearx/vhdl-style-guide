# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import constant
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_013_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_013_test_input.fixed.vhd"), lExpected)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_013(self):
        oRule = constant.rule_013()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "constant")
        self.assertEqual(oRule.identifier, "013")

        lExpected = [5, 12, 17, 17, 20]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_013(self):
        oRule = constant.rule_013()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])


lFilePackage, eErrorPackage = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_013_test_input.package.vhd"))

lExpectedPackage = []
lExpectedPackage.append("")
utils.read_file(os.path.join(sTestDir, "rule_013_test_input.package.fixed.vhd"), lExpectedPackage)


class test_rule_package(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFilePackage)
        self.assertIsNone(eErrorPackage)

    def test_rule_013_package(self):
        oRule = constant.rule_013()

        lExpected = [5, 11, 17, 17, 17]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_013_package(self):
        oRule = constant.rule_013()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpectedPackage, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])
