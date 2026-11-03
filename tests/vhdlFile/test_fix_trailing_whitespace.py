# -*- coding: utf-8 -*-
"""The trailing whitespace cleanup after phase 1 keeps whitespace that code tags turn whitespace_001 off for."""

import unittest

from mhsg import parser
from mhsg.vhdlFile import utils


def line(sCode, sTrailing, lCodeTags=()):
    oWhitespace = parser.whitespace(sTrailing)
    oWhitespace.set_code_tags(list(lCodeTags))
    return [parser.item(sCode), oWhitespace, parser.carriage_return()]


class test_fix_trailing_whitespace(unittest.TestCase):
    def values(self, lTokens):
        return [o.get_value() for o in utils.fix_trailing_whitespace(lTokens)]

    def test_removed(self):
        self.assertEqual(["a", "\n"], self.values(line("a", "   ")))

    def test_kept_in_off_region(self):
        self.assertEqual(["a", "   ", "\n"], self.values(line("a", "   ", ["all"])))
        self.assertEqual(["a", "   ", "\n"], self.values(line("a", "   ", ["whitespace_001"])))

    def test_removed_when_other_rule_off(self):
        self.assertEqual(["a", "\n"], self.values(line("a", "   ", ["length_001"])))

    def test_carriage_return_first(self):
        self.assertEqual(["\n", "a"], self.values([parser.carriage_return(), parser.item("a")]))
