# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import parameter_specification
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_502_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_502_test_input.fixed.vhd"), lExpected)


class test_rule(unittest.TestCase):
    # Issue VSG 1561: references to a loop or generate parameter keep the case of its declaration.
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_502(self):
        oRule = parameter_specification.rule_502()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "parameter_specification")
        self.assertEqual(oRule.identifier, "502")

        lExpected = [5, 9, 13]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_502(self):
        oRule = parameter_specification.rule_502()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])
