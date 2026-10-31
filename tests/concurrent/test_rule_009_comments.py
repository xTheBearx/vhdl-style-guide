# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import concurrent
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_009_test_input.comments.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_009_test_input.comments.fixed.vhd"), lExpected)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_009_aligns_comments(self):
        oRule = concurrent.rule_009()

        lExpectedLines = [7, 11]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpectedLines, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_009_aligns_comments(self):
        oRule = concurrent.rule_009()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])
