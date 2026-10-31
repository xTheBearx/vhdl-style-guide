# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import generic
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_023_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_023(self):
        oRule = generic.rule_023()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "generic")
        self.assertEqual(oRule.identifier, "023")
        self.assertTrue(oRule.disable)
        self.assertFalse(oRule.fixable)

        oRule.analyze(self.oFile)
        self.assertEqual([8, 18], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_023_section_pattern(self):
        oRule = generic.rule_023()
        oRule.section_pattern = "^-- [A-Z]"

        oRule.analyze(self.oFile)
        self.assertEqual([8, 10, 18], utils.extract_violation_lines_from_violation_object(oRule.violations))
