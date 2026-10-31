# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import procedure_call
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_401_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_401_test_input.fixed.vhd"), lExpected, False)


lFile_association_after_aggregate, eError_association_after_aggregate = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_401_test_input.association_after_aggregate.vhd"),
)

lExpected_association_after_aggregate = []
lExpected_association_after_aggregate.append("")
utils.read_file(os.path.join(sTestDir, "rule_401_test_input.association_after_aggregate.fixed.vhd"), lExpected_association_after_aggregate)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_401(self):
        oRule = procedure_call.rule_401()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "procedure_call")
        self.assertEqual(oRule.identifier, "401")
        self.assertEqual(oRule.groups, ["alignment"])

        lExpected = [20, 21, 23, 29, 31, 32]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_401(self):
        oRule = procedure_call.rule_401()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_401_association_after_aggregate(self):
        # Issue VSG 1584: a named association following an aggregate argument on the same line was used for alignment.
        self.assertIsNone(eError_association_after_aggregate)
        oRule = procedure_call.rule_401()
        oFile = vhdlFile.vhdlFile(lFile_association_after_aggregate)

        oRule.analyze(oFile)
        self.assertEqual([9, 10], utils.extract_violation_lines_from_violation_object(oRule.violations))

        oRule = procedure_call.rule_401()
        oRule.fix(oFile)
        self.assertEqual(lExpected_association_after_aggregate, oFile.get_lines())
