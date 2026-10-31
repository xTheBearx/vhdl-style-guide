# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import pragma
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_100_test_input.vhd"))

lExpected_add = []
lExpected_add.append("")
utils.read_file(os.path.join(sTestDir, "rule_100_test_input.fixed_add.vhd"), lExpected_add)

lExpected_remove = []
lExpected_remove.append("")
utils.read_file(os.path.join(sTestDir, "rule_100_test_input.fixed_remove.vhd"), lExpected_remove)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_100_is_disabled_by_default(self):
        oRule = pragma.rule_100()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "pragma")
        self.assertEqual(oRule.identifier, "100")
        self.assertTrue(oRule.disable)
        self.assertEqual(oRule.action, "add")

    def test_rule_100_add(self):
        oRule = pragma.rule_100()

        lExpected = [10, 12, 14, 15]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_100_remove(self):
        oRule = pragma.rule_100()
        oRule.action = "remove"

        # --vhdl_comp_off and --vhdl_comp_on already have no space
        lExpected = [6, 8, 12, 15]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_100_add(self):
        oRule = pragma.rule_100()

        oRule.fix(self.oFile)

        self.assertEqual(lExpected_add, self.oFile.get_lines())

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_100_remove(self):
        oRule = pragma.rule_100()
        oRule.action = "remove"

        oRule.fix(self.oFile)

        self.assertEqual(lExpected_remove, self.oFile.get_lines())

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_pragma_that_would_no_longer_match_is_not_changed(self):
        # The default patterns do not match "-- vhdl_comp_off", so adding a space would turn the pragma into a comment
        oRule = pragma.rule_100()
        oRule.analyze(self.oFile)
        lLines = utils.extract_violation_lines_from_violation_object(oRule.violations)
        self.assertNotIn(17, lLines)
        self.assertNotIn(19, lLines)
