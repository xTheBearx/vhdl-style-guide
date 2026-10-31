# -*- coding: utf-8 -*-
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import architecture, comment, constant, length, library, process
from tests import utils

# Code tags from VSG (vsg_off, vsg_on, vsg_disable_next_line) must behave the same as the mhsg_ tags.

dIndentMap = utils.read_indent_file()

sTestDir = os.path.dirname(__file__)


def read_file(sFileName, bLegacy):
    lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, sFileName))
    if bLegacy:
        lFile = [sLine.replace("-- mhsg_", "-- vsg_") for sLine in lFile]
    oFile = vhdlFile.vhdlFile(lFile)
    oFile.set_indent_map(dIndentMap)
    return oFile, eError


def get_violation_lines(oRule, oFile):
    oRule.analyze(oFile)
    return utils.extract_violation_lines_from_violation_object(oRule.violations)


def build_length_003():
    oRule = length.rule_003()
    oRule.length = 2
    return oRule


class testLegacyCodeTags(unittest.TestCase):
    def check_rules_match(self, sFileName, lRuleBuilders):
        oFile, eError = read_file(sFileName, False)
        self.assertIsNone(eError)
        oLegacyFile, eError = read_file(sFileName, True)
        self.assertIsNone(eError)

        self.assertNotEqual(oFile.get_lines(), oLegacyFile.get_lines())

        for fBuildRule in lRuleBuilders:
            self.assertEqual(get_violation_lines(fBuildRule(), oFile), get_violation_lines(fBuildRule(), oLegacyFile))

    def test_vsg_off_and_vsg_on(self):
        self.check_rules_match(
            "code_tag_test_input.vhd",
            [library.rule_002, comment.rule_010, constant.rule_016, build_length_003],
        )

    def test_vsg_disable_next_line(self):
        self.check_rules_match(
            "next_line_code_tag_test_input.vhd",
            [process.rule_016, process.rule_018, process.rule_014, architecture.rule_024, process.rule_002],
        )
