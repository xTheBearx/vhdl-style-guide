# -*- coding: utf-8 -*-
"""
case_exceptions used to apply only to words spelled exactly as listed (issue #87).
"""

import unittest

from mhsg import vhdlFile
from mhsg.rules import case_utils, library
from tests import utils

lFile = [
    "",
    "library Ieee;",
    "library std;",
    "",
    "entity foo is",
    "end entity foo;",
]


class test_case_exceptions(unittest.TestCase):
    def create_rule(self):
        oRule = library.rule_500()
        oRule.case = "lower"
        oRule.case_exceptions = ["STD", "IEEE"]
        return oRule

    def test_listed_word_in_other_case_is_reported(self):
        oRule = self.create_rule()
        oRule.analyze(vhdlFile.vhdlFile(lFile))
        self.assertEqual([2, 3], utils.extract_violation_lines_from_violation_object(oRule.violations))
        self.assertEqual(['Change "Ieee" to "IEEE"', 'Change "std" to "STD"'], [o.get_solution() for o in oRule.violations])

    def test_fix_uses_listed_spelling(self):
        oFile = vhdlFile.vhdlFile(lFile)
        oRule = self.create_rule()
        oRule.fix(oFile)
        self.assertEqual(["", "library IEEE;", "library STD;"], oFile.get_lines()[1:4])
        oRule.analyze(oFile)
        self.assertEqual([], oRule.violations)

    def test_violation_keeps_token_index(self):
        oRule = self.create_rule()
        oViolation = case_utils.check_for_exception("Ieee", oRule, None, 3, 1)
        self.assertEqual({"value": "IEEE", "index": 3}, oViolation.get_action())

    def test_listed_spelling_is_not_reported(self):
        oRule = self.create_rule()
        self.assertIsNone(case_utils.check_for_exception("IEEE", oRule, None, 0, 1))
