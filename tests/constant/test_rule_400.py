# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import config, rule_list, severity, vhdlFile
from mhsg.rules import constant
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_400_test_input.vhd"))


lFile_nested_aggregates, eError_nested_aggregates = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_400_test_input.nested_aggregates.vhd"),
)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_400_options(self):
        oRule = constant.rule_400()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "constant")
        self.assertEqual(oRule.identifier, "400")
        self.assertEqual(len(oRule.configuration), 12)

    def test_rule_400_yes_no_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        lExpected = [5, 6, 8, 9, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 32, 34, 35, 37, 38])
        lExpected.extend([42, 43, 44, 46, 48, 50, 51, 52])
        lExpected.extend([58, 59, 60, 61])
        lExpected.extend([64, 65, 66])
        lExpected.extend([72, 73, 74, 75])
        lExpected.extend([77, 78, 79, 80])
        lExpected.extend([86, 87, 88, 89, 91, 94])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_yes_no_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        oRule.fix(self.oFile)

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_yes_no_no_no_no.vhd"), lExpected)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    ###############################################################################
    def test_rule_400_no_no_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "no"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        lExpected = [5, 6, 8, 9, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 34, 35, 37, 38])
        lExpected.extend([42, 43, 46, 47, 48, 50, 51, 52])
        lExpected.extend([58, 59, 60, 61])
        lExpected.extend([64, 65, 66])
        lExpected.extend([73, 74, 75])
        lExpected.extend([77, 78, 80])
        lExpected.extend([86, 87, 88, 89, 91, 94])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_no_no_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "no"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_no_no_no_no_no.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    ###############################################################################
    def test_rule_400_yes_no_yes_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        lExpected = [5, 6, 8, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 32, 34, 35, 37, 38])
        lExpected.extend([42, 43, 44, 46, 48, 50, 51, 52])
        lExpected.extend([58, 59, 60, 61])
        lExpected.extend([64, 65, 66])
        lExpected.extend([72, 73, 74, 75])
        lExpected.extend([77, 78, 79, 80])
        lExpected.extend([86, 87, 88, 89, 91, 94])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_yes_no_yes_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "no"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_yes_no_yes_no_no.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    ###############################################################################
    def test_rule_400_yes_yes_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        lExpected = [5, 8, 9, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 32, 34, 35, 37, 38])
        lExpected.extend([42, 43, 44, 46, 48, 50, 51, 52])
        lExpected.extend([58, 59, 60, 61])
        lExpected.extend([64, 65, 66])
        lExpected.extend([72, 73, 74, 75])
        lExpected.extend([77, 78, 79, 80])
        lExpected.extend([86, 87, 88, 89, 91, 94])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_yes_yes_no_no_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "no"
        oRule.aggregate_parens_ends_group = "no"
        oRule.ignore_single_line_aggregates = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_yes_yes_no_no_no.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    ###############################################################################
    def test_rule_400_yes_yes_yes_yes_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "yes"
        oRule.ignore_single_line_aggregates = "no"

        lExpected = [5, 8, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 32, 34, 35, 37, 38])
        lExpected.extend([42, 43, 44, 46, 48, 50, 51, 52])
        lExpected.extend([72, 73, 74, 75])
        lExpected.extend([77, 78, 79, 80])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_yes_yes_yes_yes_no(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "yes"
        oRule.ignore_single_line_aggregates = "no"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_yes_yes_yes_yes_no.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    ###############################################################################
    def test_rule_400_yes_yes_yes_yes_yes(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "yes"
        oRule.ignore_single_line_aggregates = "yes"

        lExpected = [5, 8, 11]
        lExpected.extend([17, 18, 21, 22, 25, 26])
        lExpected.extend([31, 32, 34, 35, 37, 38])
        lExpected.extend([42, 43, 44, 46, 48, 50, 51, 52])
        lExpected.extend([72, 73, 74, 75])
        lExpected.extend([77, 78, 79, 80])
        lExpected.extend([94])

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_yes_yes_yes_yes_yes(self):
        oRule = constant.rule_400()
        oRule.compact_alignment = "yes"
        oRule.blank_line_ends_group = "yes"
        oRule.comment_line_ends_group = "yes"
        oRule.aggregate_parens_ends_group = "yes"
        oRule.ignore_single_line_aggregates = "yes"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_400_test_input.fixed_yes_yes_yes_yes_yes.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_400_per_level_is_default(self):
        # Issue VSG 1502: each aggregate is aligned on its own, which keeps the outer associations aligned.
        self.assertIsNone(eError_nested_aggregates)
        oRule = constant.rule_400()
        self.assertEqual(oRule.aggregate_parens_ends_group, "per_level")

        oFile = vhdlFile.vhdlFile(lFile_nested_aggregates)
        oRule.analyze(oFile)
        self.assertEqual([], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_per_level_misaligned_outer_associations(self):
        lMisaligned = [sLine.replace("c_control_reg_idx         =>", "c_control_reg_idx =>") for sLine in lFile_nested_aggregates]
        oFile = vhdlFile.vhdlFile(lMisaligned)
        oRule = constant.rule_400()

        oRule.analyze(oFile)
        self.assertEqual([12], utils.extract_violation_lines_from_violation_object(oRule.violations))

        oRule = constant.rule_400()
        oRule.fix(oFile)
        self.assertEqual([""] + lFile_nested_aggregates, oFile.get_lines())

    def test_fix_all_rules_converges_with_nested_aggregates(self):
        # With the reporter's constant_016 configuration, every --fix used to move the code further right.
        oConfig = config.config()
        oConfig.dConfig = {
            "rule": {
                "constant_016": {
                    "first_paren_new_line": "yes",
                    "last_paren_new_line": "yes",
                    "assign_on_single_line": "ignore",
                    "open_paren_new_line": "yes",
                    "close_paren_new_line": "yes",
                },
            },
        }
        oConfig.severity_list = severity.create_list({})

        lLines = lFile_nested_aggregates
        lResults = []
        for iRun in range(2):
            oFile = vhdlFile.vhdlFile(lLines)
            oFile.set_indent_map(utils.read_indent_file())
            oRuleList = rule_list.rule_list(oFile, oConfig.severity_list)
            oRuleList.configure(oConfig)
            oRuleList.fix()
            lLines = oFile.get_lines()[1:]
            lResults.append(lLines)

        self.assertEqual(lResults[0], lResults[1])
