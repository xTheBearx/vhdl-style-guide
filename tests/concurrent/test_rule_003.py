# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import concurrent, constant
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_003_test_input.vhd"))

dIndentMap = utils.read_indent_file()

lExpected_align_left_no_align_paren_no = []
lExpected_align_left_no_align_paren_no.append("")
utils.read_file(os.path.join(sTestDir, "rule_003_test_input.fixed_align_left_no_align_paren_no.vhd"), lExpected_align_left_no_align_paren_no)

lExpected_align_left_no_align_paren_yes = []
lExpected_align_left_no_align_paren_yes.append("")
utils.read_file(os.path.join(sTestDir, "rule_003_test_input.fixed_align_left_no_align_paren_yes.vhd"), lExpected_align_left_no_align_paren_yes)

lExpected_align_left_yes_align_paren_no = []
lExpected_align_left_yes_align_paren_no.append("")
utils.read_file(os.path.join(sTestDir, "rule_003_test_input.fixed_align_left_yes_align_paren_no.vhd"), lExpected_align_left_yes_align_paren_no)

lExpected_align_left_yes_align_paren_yes = []
lExpected_align_left_yes_align_paren_yes.append("")
utils.read_file(os.path.join(sTestDir, "rule_003_test_input.fixed_align_left_yes_align_paren_yes.vhd"), lExpected_align_left_yes_align_paren_yes)


lFile_on_new_line_after_assign, eError_on_new_line_after_assign = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_003_test_input.on_new_line_after_assign.vhd"),
)

lExpected_on_new_line_after_assign = []
lExpected_on_new_line_after_assign.append("")
utils.read_file(os.path.join(sTestDir, "rule_003_test_input.on_new_line_after_assign.fixed.vhd"), lExpected_on_new_line_after_assign)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)
        self.oFile.set_indent_map(dIndentMap)

    def test_rule_003_align_left_no_align_paren_yes(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "no"
        oRule.align_paren = "yes"
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "concurrent")
        self.assertEqual(oRule.identifier, "003")

        lExpected = [9, 13, 45, 48, 49, 52, 53, 56, 57, 58, 66, 67, 70, 71, 74, 75, 76, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_align_left_false_align_paren_true(self):
        oRule = concurrent.rule_003()
        oRule.align_left = False
        oRule.align_paren = True
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "concurrent")
        self.assertEqual(oRule.identifier, "003")

        lExpected = [9, 13, 45, 48, 49, 52, 53, 56, 57, 58, 66, 67, 70, 71, 74, 75, 76, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_003_align_left_no_align_paren_yes(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "no"
        oRule.align_paren = "yes"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_align_left_no_align_paren_yes, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_003_align_left_yes_align_paren_no(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "yes"
        oRule.align_paren = "no"

        lExpected = [9, 12, 13, 16, 17, 20, 21, 22, 27, 30, 31, 34, 35, 38, 39, 40, 63, 67, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_align_left_true_align_paren_false(self):
        oRule = concurrent.rule_003()
        oRule.align_left = True
        oRule.align_paren = False

        lExpected = [9, 12, 13, 16, 17, 20, 21, 22, 27, 30, 31, 34, 35, 38, 39, 40, 63, 67, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_003_align_left_yes_align_paren_no(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "yes"
        oRule.align_paren = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_align_left_yes_align_paren_no, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_003_align_left_yes_align_paren_yes(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "yes"
        oRule.align_paren = "yes"

        lExpected = [9, 12, 13, 16, 17, 20, 21, 22, 30, 31, 34, 35, 38, 39, 40, 45, 49, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_align_left_true_align_paren_true(self):
        oRule = concurrent.rule_003()
        oRule.align_left = True
        oRule.align_paren = True

        lExpected = [9, 12, 13, 16, 17, 20, 21, 22, 30, 31, 34, 35, 38, 39, 40, 45, 49, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_003_align_left_yes_align_paren_yes(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "yes"
        oRule.align_paren = "yes"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_align_left_yes_align_paren_yes, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_003_align_left_no_align_paren_no(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "no"
        oRule.align_paren = "no"

        lExpected = [27, 31, 45, 48, 49, 52, 53, 56, 57, 58, 63, 66, 67, 70, 71, 74, 75, 76, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_align_left_false_align_paren_false(self):
        oRule = concurrent.rule_003()
        oRule.align_left = False
        oRule.align_paren = False

        lExpected = [27, 31, 45, 48, 49, 52, 53, 56, 57, 58, 63, 66, 67, 70, 71, 74, 75, 76, 81]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_003_align_left_no_align_paren_no(self):
        oRule = concurrent.rule_003()
        oRule.align_left = "no"
        oRule.align_paren = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_align_left_no_align_paren_no, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_003_on_new_line_after_assign(self):
        # Issue VSG 1582: indent one level when the expression starts on a new line after the assignment,
        # otherwise align after the assignment operator.
        self.assertIsNone(eError_on_new_line_after_assign)
        oFile = vhdlFile.vhdlFile(lFile_on_new_line_after_assign)
        oFile.set_indent_map(dIndentMap)

        lRules = [concurrent.rule_003(), constant.rule_014()]
        for oRule in lRules:
            oRule.align_left = "on_new_line_after_assign"
            oRule.align_paren = "yes"
            oRule.fix(oFile)

        self.assertEqual(lExpected_on_new_line_after_assign, oFile.get_lines())
