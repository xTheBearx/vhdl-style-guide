# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import architecture
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_027_test_input.vhd"))


lFile_delimited_comment, eError_delimited_comment = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_027_test_input.delimited_comment.vhd"),
)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_027(self):
        oRule = architecture.rule_027()

        lExpected = []
        lExpected.extend(range(3, 7))
        lExpected.extend(range(9, 11))
        lExpected.extend(range(12, 14))
        lExpected.extend(range(15, 17))
        lExpected.extend(range(18, 20))
        lExpected.extend(range(21, 23))
        lExpected.extend(range(24, 26))

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_027(self):
        oRule = architecture.rule_027()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_027_test_input.fixed.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_027_delimited_comment(self):
        # Issue VSG 1573: the closing line of a multi-line delimited comment was aligned with inline comments,
        # moving the comments one column further on every fix.
        self.assertIsNone(eError_delimited_comment)
        oRule = architecture.rule_027()
        oRule.blank_line_ends_group = "yes"
        oFile = vhdlFile.vhdlFile(lFile_delimited_comment)

        oRule.analyze(oFile)
        self.assertEqual([], utils.extract_violation_lines_from_violation_object(oRule.violations))
