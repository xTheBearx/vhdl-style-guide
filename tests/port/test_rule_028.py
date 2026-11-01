# -*- coding: utf-8 -*-

import copy
import importlib
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import port
from tests import utils

# The module, since mhsg.rules.port.rule_028 is the rule class
rule_028_module = importlib.import_module("mhsg.rules.port.rule_028")

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


class test_clock_reset_words(unittest.TestCase):
    def setUp(self):
        self.oRule = port.rule_028()

    def assert_rank(self, iRank, lNames):
        for sName in lNames:
            with self.subTest(sName):
                self.assertEqual(iRank, self.oRule._clock_reset_rank(sName))

    def test_clocks(self):
        self.assert_rank(
            0,
            ["clk", "CLK", "i_clk", "clk_i", "sys_clk", "s_axi_aclk", "clk_100mhz", "clk100", "clk_p", "clock", "pclk", "clock0", "clkout", "clockin"],
        )

    def test_resets(self):
        self.assert_rank(
            1,
            ["rst", "rst_n", "rstn", "i_rst", "s_axi_aresetn", "arst", "srst_n", "reset", "rst_sync", "nreset", "rst90", "rstb", "cpu_rstb", "presetn"],
        )

    def test_qualified_names_are_neither(self):
        self.assert_rank(2, ["clk_en", "clk_en_i", "clk_sel", "clk_locked", "clk_div", "clock_ena", "clocken0", "rst_done", "reset_req", "rst_cnt"])

    def test_other_ports(self):
        self.assert_rank(2, ["data", "first", "burst", "preset_value", "block", "valid", "a_i"])

    def test_custom_words(self):
        self.oRule.clock_words = ["ck"]
        self.oRule.qualifier_words = []
        self.assert_rank(0, ["ck", "sys_ck"])
        self.assert_rank(2, ["clk"])
        self.assert_rank(1, ["rst_done"])


class test_differential_pairs(unittest.TestCase):
    def sort(self, oRule, lNames):
        lElements = [{"names": [sName], "mode": "in"} for sName in lNames]
        oRule._dPairs = rule_028_module.get_differential_pairs(lElements, oRule.differential_suffixes)
        return [dElement["names"][0] for dElement in sorted(lElements, key=oRule._sort_key)]

    def test_transceiver_reference_clocks(self):
        oRule = port.rule_028()
        for sName in ["mgtrefclk0_p", "gt_refclk1_n"]:
            with self.subTest(sName):
                self.assertEqual(0, oRule._clock_reset_rank(sName))

    def test_positive_before_negative(self):
        oRule = port.rule_028()
        self.assertEqual(
            ["sys_clk_p", "sys_clk_n", "rst_n", "data", "rx_p", "rx_n"],
            self.sort(oRule, ["rx_n", "sys_clk_n", "data", "rst_n", "rx_p", "sys_clk_p"]),
        )

    def test_custom_suffixes(self):
        oRule = port.rule_028()
        oRule.differential_suffixes = [["_pos", "_neg"]]
        self.assertEqual(["lvds_pos", "lvds_neg", "rx_n", "rx_p"], self.sort(oRule, ["rx_p", "lvds_neg", "rx_n", "lvds_pos"]))
