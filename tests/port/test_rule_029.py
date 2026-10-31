# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import port
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_029_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_029(self):
        oRule = port.rule_029()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "port")
        self.assertEqual(oRule.identifier, "029")
        self.assertTrue(oRule.disable)
        self.assertFalse(oRule.fixable)

        oRule.analyze(self.oFile)
        self.assertEqual([8], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_029_section_pattern(self):
        oRule = port.rule_029()
        oRule.section_pattern = "^-- [A-Z]"

        # "-- unformatted note" does not match, and a border of dashes does not either
        oRule.analyze(self.oFile)
        self.assertEqual([8, 15], utils.extract_violation_lines_from_violation_object(oRule.violations))
