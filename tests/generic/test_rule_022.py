# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import generic
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_022_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_022(self):
        oRule = generic.rule_022()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "generic")
        self.assertEqual(oRule.identifier, "022")
        self.assertTrue(oRule.disable)
        self.assertFalse(oRule.fixable)

        lExpected = [28, 37]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

        self.assertEqual(oRule.violations[0].sSolution, "Order generics alphabetically: G_DEPTH, G_WIDTH")
        self.assertEqual(oRule.violations[1].sSolution, "Order generics alphabetically: G_ADDR_WIDTH, G_DEPTH, G_WIDTH")
