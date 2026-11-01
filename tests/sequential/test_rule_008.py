# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import sequential
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_008_test_input.vhd"))

lExpected_new_line_after_assign_yes = []
lExpected_new_line_after_assign_yes.append("")
utils.read_file(os.path.join(sTestDir, "rule_008_test_input.fixed_new_line_after_assign_yes.vhd"), lExpected_new_line_after_assign_yes)

lExpected_new_line_after_assign_no = []
lExpected_new_line_after_assign_no.append("")
utils.read_file(os.path.join(sTestDir, "rule_008_test_input.fixed_new_line_after_assign_no.vhd"), lExpected_new_line_after_assign_no)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_008_new_line_after_assign_yes(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = "yes"
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "sequential")
        self.assertEqual(oRule.identifier, "008")
        self.assertEqual(oRule.groups, ["structure"])

        lExpected = [22, 25]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_008_new_line_after_assign_true(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = True
        self.assertTrue(oRule)

        lExpected = [22, 25]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_008_new_line_after_assign_yes(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = "yes"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_new_line_after_assign_yes, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_008_new_line_after_assign_no(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = "no"

        lExpected = [11, 15]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_008_new_line_after_assign_false(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = False

        lExpected = [11, 15]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_008_new_line_after_assign_no(self):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_new_line_after_assign_no, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])


lSingleLine = [
    "",
    "architecture RTL of FIFO is",
    "",
    "begin",
    "",
    "  process",
    "  begin",
    "",
    "    a <= b or d;",
    "",
    "  end process;",
    "",
    "end architecture RTL;",
]


class test_rule_ignore_single_line(unittest.TestCase):
    """ignore_single_line: no used to have no effect (issue #85)."""

    def check(self, oIgnoreSingleLine, lExpected):
        oRule = sequential.rule_008()
        oRule.new_line_after_assign = "yes"
        oRule.ignore_single_line = oIgnoreSingleLine
        oRule.analyze(vhdlFile.vhdlFile(lSingleLine))
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_yes(self):
        self.check("yes", [])

    def test_true(self):
        self.check(True, [])

    def test_no(self):
        self.check("no", [9])

    def test_false(self):
        self.check(False, [9])
