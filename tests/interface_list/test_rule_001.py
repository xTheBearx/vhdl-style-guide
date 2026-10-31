# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import interface_list
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_001_test_input.vhd"))

lExpected_remove = []
lExpected_remove.append("")
utils.read_file(os.path.join(sTestDir, "rule_001_test_input.fixed_remove.vhd"), lExpected_remove)

lExpected_add = []
lExpected_add.append("")
utils.read_file(os.path.join(sTestDir, "rule_001_test_input.fixed_add.vhd"), lExpected_add)


class test_rule(unittest.TestCase):
    """
    VSG issue 1480: the optional VHDL-2019 semicolon after the last element of an interface list.
    """

    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_001_remove(self):
        oRule = interface_list.rule_001()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "interface_list")
        self.assertEqual(oRule.identifier, "001")
        self.assertTrue(oRule.disable)
        self.assertEqual(oRule.action, "remove")

        lExpected = [16, 22]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_001_remove(self):
        oRule = interface_list.rule_001()

        oRule.fix(self.oFile)

        self.assertEqual(lExpected_remove, self.oFile.get_lines())

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_001_add(self):
        oRule = interface_list.rule_001()
        oRule.action = "add"

        lExpected = [4, 8, 27]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_001_add(self):
        oRule = interface_list.rule_001()
        oRule.action = "add"

        oRule.fix(self.oFile)

        self.assertEqual(lExpected_add, self.oFile.get_lines())

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])
