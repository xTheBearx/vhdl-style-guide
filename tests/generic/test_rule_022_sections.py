# -*- coding: utf-8 -*-

import copy
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
        self.assertEqual("Order generics alphabetically: G_DEPTH, G_WIDTH (not moved: move_generics is never)", oRule.violations[0].get_solution())

    def test_rule_022_whole_list(self):
        oRule = generic.rule_022()
        oRule.sort_within_sections = "no"

        # G_ADDR_WIDTH uses G_DEPTH, so it stays after it
        oRule.analyze(self.oFile)
        self.assertEqual([5], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual(
            "Order generics alphabetically: G_DEBUG, G_DEPTH, G_ADDR_WIDTH, G_WIDTH (not moved: move_generics is never)",
            oRule.violations[0].get_solution(),
        )

    def test_fix_rule_022_within_sections_when_safe(self):
        oRule = generic.rule_022()
        oRule.move_generics = "when_safe"
        self.oFile.configuration = copy.copy(self.oFile.configuration)
        self.oFile.configuration.project_positional_generic_entities = set()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()
        self.assertEqual("    G_DEPTH      : integer := 16;", lActual[5])
        self.assertEqual("    G_WIDTH      : integer := 8;", lActual[6])
        # G_ADDR_WIDTH uses G_DEPTH, but they are in different sections, so the second section is in order
        self.assertEqual("    G_ADDR_WIDTH : integer := G_DEPTH / 4;", lActual[9])
        oRule.analyze(self.oFile)
        self.assertEqual([], oRule.violations)

    def test_fix_rule_022_whole_list_separated_by_sections(self):
        oRule = generic.rule_022()
        oRule.move_generics = "when_safe"
        oRule.sort_within_sections = "no"
        self.oFile.configuration = copy.copy(self.oFile.configuration)
        self.oFile.configuration.project_positional_generic_entities = set()

        oRule.analyze(self.oFile)
        self.assertIn("separated by blank lines or comments", oRule.violations[0].get_solution())
