# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import generic
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_022_test_input.sections.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_022_within_sections(self):
        oRule = generic.rule_022()

        oRule.analyze(self.oFile)
        self.assertEqual([5], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order generics alphabetically: G_DEPTH, G_WIDTH", oRule.violations[0].get_solution())

    def test_rule_022_whole_list(self):
        oRule = generic.rule_022()
        oRule.sort_within_sections = "no"

        # G_ADDR_WIDTH uses G_DEPTH, so it stays after it
        oRule.analyze(self.oFile)
        self.assertEqual([5], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order generics alphabetically: G_DEBUG, G_DEPTH, G_ADDR_WIDTH, G_WIDTH", oRule.violations[0].get_solution())
