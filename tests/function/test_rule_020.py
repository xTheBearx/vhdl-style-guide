# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import function
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_020_test_input.vhd"))


lFile_nested, eError_nested = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_020_test_input.nested.vhd"))

lExpected_nested = []
lExpected_nested.append("")
utils.read_file(os.path.join(sTestDir, "rule_020_test_input.nested.fixed.vhd"), lExpected_nested)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_020_add(self):
        oRule = function.rule_020()
        oRule.action = "add"

        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "function")
        self.assertEqual(oRule.identifier, "020")
        self.assertEqual(oRule.groups, ["structure", "structure::optional"])

        lExpected = [26, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_020_add(self):
        oRule = function.rule_020()
        oRule.action = "add"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_020_test_input.fixed_add.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_020_remove(self):
        oRule = function.rule_020()
        oRule.action = "remove"

        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "function")
        self.assertEqual(oRule.identifier, "020")
        self.assertEqual(oRule.groups, ["structure", "structure::optional"])

        lExpected = [18, 22]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_020_remove(self):
        oRule = function.rule_020()
        oRule.action = "remove"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_020_test_input.fixed_remove.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_020_nested(self):
        # Issue VSG 1522: designators added to nested subprograms overwrote each other and produced invalid code.
        self.assertIsNone(eError_nested)
        oRule = function.rule_020()
        oFile = vhdlFile.vhdlFile(lFile_nested)

        oRule.fix(oFile)
        self.assertEqual(lExpected_nested, oFile.get_lines())

        oRule.analyze(oFile)
        self.assertEqual(oRule.violations, [])
