# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import comment
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_013_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_013(self):
        oRule = comment.rule_013()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "comment")
        self.assertEqual(oRule.identifier, "013")
        self.assertTrue(oRule.disable)
        self.assertFalse(oRule.fixable)

        lExpected = [30, 31, 32, 33, 34, 35, 36, 37, 38]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))
