# -*- coding: utf-8 -*-

import copy
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import port
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_028_test_input.vhd"))

lUnchanged = []
lUnchanged.append("")
utils.read_file(os.path.join(sTestDir, "rule_028_test_input.vhd"), lUnchanged)

lExpected_when_safe = []
lExpected_when_safe.append("")
utils.read_file(os.path.join(sTestDir, "rule_028_test_input.fixed_when_safe.vhd"), lExpected_when_safe)


def create_file(lPositional):
    """Returns the test file, with the entities instantiated with positional association in the run."""
    oFile = vhdlFile.vhdlFile(lFile)
    oFile.configuration = copy.copy(oFile.configuration)
    oFile.configuration.project_positional_entities = lPositional
    return oFile


class test_rule(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(eError)

    def test_rule_028(self):
        oRule = port.rule_028()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "port")
        self.assertEqual(oRule.identifier, "028")
        self.assertTrue(oRule.disable)

        oRule.analyze(create_file(set()))
        self.assertEqual([5, 9, 18, 29], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order ports: clk, a_i, data_o (not moved: move_ports is never)", oRule.violations[0].get_solution())

    def test_rule_028_order_by_name(self):
        oRule = port.rule_028()
        oRule.order = ["name"]

        oRule.analyze(create_file(set()))
        self.assertEqual([5, 9, 18, 29, 37], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order ports: a_i, clk, data_o (not moved: move_ports is never)", oRule.violations[0].get_solution())

    def test_rule_028_whole_port_list(self):
        oRule = port.rule_028()
        oRule.sort_within_sections = "no"

        oRule.analyze(create_file(set()))
        self.assertEqual([5, 18, 29], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order ports: clk, rst, rst_n, a_i, data_o (not moved: move_ports is never)", oRule.violations[0].get_solution())

    def test_fix_rule_028_move_ports_never(self):
        oRule = port.rule_028()
        oFile = create_file(set())

        oRule.fix(oFile)

        self.assertEqual(lUnchanged, oFile.get_lines())

    def test_fix_rule_028_when_safe(self):
        oRule = port.rule_028()
        oRule.move_ports = "when_safe"
        oFile = create_file(set())

        oRule.fix(oFile)

        self.assertEqual(lExpected_when_safe, oFile.get_lines())

        # The component and the declaration that spans two lines are reported, but not moved
        oRule.analyze(oFile)
        self.assertEqual([18, 29], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertIn("ports of component declarations are not moved", oRule.violations[0].get_solution())
        self.assertIn("a port declaration is not on a line of its own", oRule.violations[1].get_solution())

    def test_fix_rule_028_entity_instantiated_by_position(self):
        oRule = port.rule_028()
        oRule.move_ports = "when_safe"
        oFile = create_file({"top"})

        oRule.fix(oFile)

        self.assertEqual(lUnchanged, oFile.get_lines())

    def test_fix_rule_028_instances_not_known(self):
        # For example input from stdin, where the other files of the project are not known
        oRule = port.rule_028()
        oRule.move_ports = "when_safe"
        oFile = create_file(None)

        oRule.fix(oFile)

        self.assertEqual(lUnchanged, oFile.get_lines())
