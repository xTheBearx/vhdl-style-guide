# -*- coding: utf-8 -*-
"""
Tests for the helpers of the lint model.
"""

import unittest

from mhsg import vhdlFile
from mhsg.lint import model


def condition(sCondition):
    """Returns the tokens of an if condition."""
    oFile = vhdlFile.vhdlFile(
        [
            "",
            "architecture a of e is",
            "begin",
            "  process is",
            "  begin",
            f"    if {sCondition} then",
            "      null;",
            "    end if;",
            "  end process;",
            "end architecture;",
        ],
    )
    oIf = oFile.get_lint_model().architectures[0].processes[0].statements[0]
    return oIf.branches[0][0]


class test_model(unittest.TestCase):
    def test_reset_condition(self):
        self.assertEqual(("rst", "1"), model.reset_condition(condition("rst = '1'")))
        self.assertEqual(("rst_n", "0"), model.reset_condition(condition("rst_n = '0'")))
        self.assertEqual(("rst", "0"), model.reset_condition(condition("rst /= '1'")))
        self.assertEqual(("rst", "0"), model.reset_condition(condition("not rst")))
        self.assertEqual(("rst", "1"), model.reset_condition(condition("(rst)")))
        self.assertEqual(("rst", None), model.reset_condition(condition("RST_ASYNC_G and rst = RST_POLARITY_G")))
        self.assertIsNone(model.reset_condition(condition("a = '1' and b = '1'")))

    def test_edges(self):
        self.assertEqual([("clk", "rising")], model.edges(condition("rising_edge(clk)")))
        self.assertEqual([("clk", "falling")], model.edges(condition("falling_edge(clk)")))
        self.assertEqual([("clk", "event")], model.edges(condition("clk'event and clk = '1'")))
        self.assertEqual([], model.edges(condition("a = b")))

    def test_names_skip_static_attribute_prefixes(self):
        self.assertEqual(["b"], model.names(condition("a'length = b")))
        self.assertEqual(["clk", "clk"], model.names(condition("clk'event and clk = '1'")))

    def test_covered(self):
        self.assertTrue(model.covered("out2(3)", {"out2"}))
        self.assertTrue(model.covered("r.f", {"r"}))
        self.assertTrue(model.covered("r.f", {"r.f"}))
        self.assertFalse(model.covered("out2", {"out2(3)"}))
        self.assertFalse(model.covered("r.f", {"r.g"}))

    def test_overlaps(self):
        self.assertTrue(model.overlaps("r.f", "r"))
        self.assertTrue(model.overlaps("r", "r.f"))
        self.assertFalse(model.overlaps("r.f", "r.g"))
        self.assertFalse(model.overlaps("ab", "a"))

    def test_opposite(self):
        self.assertTrue(model.opposite("g", "not g"))
        self.assertTrue(model.opposite("g = true", "g = false"))
        self.assertTrue(model.opposite("g = '1'", "g = '0'"))
        self.assertTrue(model.opposite("a = b", "a /= b"))
        self.assertFalse(model.opposite("g", "h"))

    def test_metavalue_choice(self):
        self.assertTrue(model.is_metavalue_choice('"10x"'))
        self.assertTrue(model.is_metavalue_choice("'z'"))
        self.assertFalse(model.is_metavalue_choice('"101"'))
        self.assertFalse(model.is_metavalue_choice("idle"))

    def test_model_is_rebuilt_after_an_update(self):
        oFile = vhdlFile.vhdlFile(["", "architecture a of e is", "begin", "end architecture;"])
        oModel = oFile.get_lint_model()
        self.assertIs(oModel, oFile.get_lint_model())
        oFile.clear_declarations()
        self.assertIsNot(oModel, oFile.get_lint_model())
