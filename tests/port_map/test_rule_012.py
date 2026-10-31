# -*- coding: utf-8 -*-

import copy
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import port_map
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_012_test_input.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_012_test_input.fixed.vhd"), lExpected)

lExpected_name = []
lExpected_name.append("")
utils.read_file(os.path.join(sTestDir, "rule_012_test_input.fixed_name.vhd"), lExpected_name)

# The entity sub is declared in another file of the run
dPortOrders = {"entity": {"sub": ("clk", "data", "q")}, "component": {}}


def create_file(dPorts):
    oFile = vhdlFile.vhdlFile(lFile)
    oFile.configuration = copy.copy(oFile.configuration)
    oFile.configuration.project_port_orders = dPorts
    return oFile


class test_rule(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(eError)

    def test_rule_012(self):
        oRule = port_map.rule_012()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "port_map")
        self.assertEqual(oRule.identifier, "012")
        self.assertTrue(oRule.disable)

        oRule.analyze(create_file(dPortOrders))
        self.assertEqual([18, 24, 28], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual("Order associations as in the declaration of sub: clk, data, data, q", oRule.violations[0].get_solution())

    def test_rule_012_declaration_not_known(self):
        # Only the component declared in the file is known
        oRule = port_map.rule_012()

        oRule.analyze(create_file(None))
        self.assertEqual([24], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_012_declared_differently_in_several_files(self):
        oRule = port_map.rule_012()

        oRule.analyze(create_file({"entity": {"sub": None}, "component": {}}))
        self.assertEqual([24], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_rule_012_order_by_name(self):
        oRule = port_map.rule_012()
        oRule.order = "name"

        oRule.analyze(create_file(dPortOrders))
        self.assertEqual([18, 24, 28, 35], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_012(self):
        oRule = port_map.rule_012()
        oFile = create_file(dPortOrders)

        oRule.fix(oFile)

        self.assertEqual(lExpected, oFile.get_lines())

        oRule.analyze(oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_012_order_by_name(self):
        oRule = port_map.rule_012()
        oRule.order = "name"
        oFile = create_file(dPortOrders)

        oRule.fix(oFile)

        self.assertEqual(lExpected_name, oFile.get_lines())

        oRule.analyze(oFile)
        self.assertEqual(oRule.violations, [])
