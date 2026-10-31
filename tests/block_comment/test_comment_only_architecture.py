# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import rule_list, severity, vhdlFile
from mhsg.rules import block_comment
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "comment_only_architecture.vhd"))

dIndentMap = utils.read_indent_file()


class test_comment_only_architecture(unittest.TestCase):
    # Issue VSG 1571: a block comment followed only by comments before the end of the architecture was given the
    # indent of the end keyword when analyzed, but the block comment indent when fixed, so the two disagreed.
    def setUp(self):
        self.assertIsNone(eError)
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.oFile.set_indent_map(dIndentMap)

    def test_block_comment_header_and_footer(self):
        for oRule in [block_comment.rule_001(), block_comment.rule_003()]:
            oRule.analyze(self.oFile)
            self.assertEqual([], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_check_agrees_with_fix(self):
        oRuleList = rule_list.rule_list(self.oFile, severity.create_list({}))
        for oRule in oRuleList.rules:
            if oRule.unique_id in ["block_comment_001", "block_comment_002", "block_comment_003"]:
                oRule.disable = False
        oRuleList.check_rules(bAllPhases=True)
        lCheck = [dViolation["rule"] for dViolation in oRuleList.extract_violation_dictionary()["violations"]]
        self.assertNotIn("block_comment_001", lCheck)
        self.assertNotIn("block_comment_003", lCheck)
        self.assertEqual(
            [10],
            [dViolation["linenumber"] for dViolation in oRuleList.extract_violation_dictionary()["violations"] if dViolation["rule"] == "comment_010"],
        )
