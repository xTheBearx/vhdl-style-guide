# -*- coding: utf-8 -*-
"""
Tests for the label rules used by DO-254 check DR1: concurrent_013, case_022 and case_023.
"""

import unittest

from mhsg import vhdlFile
from mhsg.rules import case, concurrent

lFile = [
    "",
    "architecture rtl of fifo is",
    "begin",
    "  a <= b;",
    "  label_c : c <= d;",
    "  e <= f when g = '1' else h;",
    "  process (b) is",
    "  begin",
    "    case b is",
    "      when others => null;",
    "    end case;",
    "    decode : case b is",
    "      when others => null;",
    "    end case;",
    "    decode2 : case b is",
    "      when others => null;",
    "    end case decode2;",
    "  end process;",
    "end architecture rtl;",
]


def lines(oRule):
    oRule.analyze(vhdlFile.vhdlFile(lFile))
    return [o.get_line_number() for o in oRule.violations]


class test_label_rules(unittest.TestCase):
    def test_concurrent_013(self):
        self.assertEqual([4, 6], lines(concurrent.rule_013()))

    def test_case_022(self):
        self.assertEqual([9], lines(case.rule_022()))

    def test_case_023(self):
        oRule = case.rule_023()
        self.assertEqual([14], lines(oRule))
        self.assertEqual("Add decode after end case", oRule.violations[0].get_solution())

    def test_disabled_and_not_fixable(self):
        for oRule in (concurrent.rule_013(), case.rule_022(), case.rule_023()):
            with self.subTest(oRule.unique_id):
                self.assertTrue(oRule.disable)
                self.assertFalse(oRule.fixable)
