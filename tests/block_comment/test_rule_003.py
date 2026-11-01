# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import block_comment
from tests import utils

sTestDir = os.path.dirname(__file__)

dIndentMap = utils.read_indent_file()

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_003_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)
        self.oFile.set_indent_map(dIndentMap)

    def test_rule_003_default(self):
        oRule = block_comment.rule_003()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "block_comment")
        self.assertEqual(oRule.identifier, "003")

        lExpected = [8, 12, 16, 20, 24, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_default_wo_allow_indenting(self):
        oRule = block_comment.rule_003()
        oRule.allow_indenting = "no"

        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "block_comment")
        self.assertEqual(oRule.identifier, "003")

        lExpected = [8, 12, 16, 20, 24, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_plus(self):
        oRule = block_comment.rule_003()
        oRule.footer_left = "+"
        oRule.max_footer_column = 80

        lExpected = [4, 12, 16, 20, 24]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_bar(self):
        oRule = block_comment.rule_003()
        oRule.footer_left = "|"
        oRule.max_footer_column = 80

        lExpected = [4, 8, 16, 20, 24, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_bar_w_footer_string_centered(self):
        oRule = block_comment.rule_003()
        oRule.footer_left = "|"
        oRule.max_footer_column = 80
        oRule.footer_string = "[ abcdef ]"
        oRule.footer_right_repeat = "="
        oRule.footer_alignment = "center"

        lExpected = [4, 8, 12, 20, 24, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_bar_w_footer_string_left_justified(self):
        oRule = block_comment.rule_003()
        oRule.footer_left = "|"
        oRule.max_footer_column = 80
        oRule.footer_string = "[ abcdef ]"
        oRule.footer_right_repeat = "="
        oRule.footer_alignment = "left"

        lExpected = [4, 8, 12, 16, 24, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_003_bar_w_footer_string_right_justified(self):
        oRule = block_comment.rule_003()
        oRule.footer_left = "|"
        oRule.max_footer_column = 80
        oRule.footer_string = "[ abcdef ]"
        oRule.footer_right_repeat = "="
        oRule.footer_alignment = "right"

        lExpected = [4, 8, 12, 16, 20, 30]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))


lIndentedBlock = [
    "",
    "architecture rtl of fifo is",
    "",
    "begin",
    "",
    "  process",
    "  begin",
    "",
    "    " + "-" * 76,
    "    -- Comment",
    "    " + "-" * 76,
    "",
    "    a <= b;",
    "",
    "  end process;",
    "",
    "end architecture rtl;",
]


class test_rule_allow_indenting(unittest.TestCase):
    """allow_indenting: no used to have no effect on block_comment_002 and 003 (issue #86)."""

    def analyze(self, oRule, oAllowIndenting):
        oFile = vhdlFile.vhdlFile(lIndentedBlock)
        oFile.set_indent_map(dIndentMap)
        oFile.set_token_indent()
        oRule.allow_indenting = oAllowIndenting
        oRule.analyze(oFile)
        return oFile

    def check_footer(self, oAllowIndenting, lExpected):
        oRule = block_comment.rule_003()
        oRule.max_footer_column = 80
        self.analyze(oRule, oAllowIndenting)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_footer_with_indenting(self):
        self.check_footer("yes", [])
        self.check_footer(True, [])

    def test_footer_without_indenting(self):
        # Without indenting the footer is measured from column 0, so it is four characters short
        self.check_footer("no", [11])
        self.check_footer(False, [11])

    def test_comment_indent_without_indenting(self):
        for oAllowIndenting in ("no", False):
            with self.subTest(oAllowIndenting):
                oFile = self.analyze(block_comment.rule_002(), oAllowIndenting)
                self.assertEqual(0, oFile.lAllObjects[[o.get_value() for o in oFile.lAllObjects].index("-- Comment")].get_indent())
