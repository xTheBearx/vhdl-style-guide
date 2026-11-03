# -*- coding: utf-8 -*-
"""Tool qualification, see mhsg/qualify.py."""

import os
import unittest
from unittest import mock

from mhsg import qualify

sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class test_qualify(unittest.TestCase):
    def test_cases_pass_and_fail(self):
        # One case whose expected result is the one recorded, one with a finding that does not happen
        dManifest = qualify.load("do254")
        dCase = next(d for d in dManifest["cases"] if d["rule"] == "lint_009" and d["expected"])
        dWrong = dict(dCase, expected=dCase["expected"] + [[1, "A finding that does not happen"]])
        with mock.patch.object(qualify, "load", return_value={"cases": [dCase, dWrong]}):
            dReport = qualify.run("do254", 2)
        self.assertEqual({qualify.PASS: 1, qualify.FAIL: 1, qualify.NOT_RUN: 0}, dReport["summary"])
        self.assertEqual(["DO254-SS4"], dReport["cases"][0]["checks"])
        self.assertEqual(dCase["expected"], dReport["cases"][1]["actual"])
        self.assertIn("lint_001", dReport["rules_without_cases"])
        sText = qualify.text(dReport, {"mhsg": "1", "python": "3", "command_line": [], "configuration_files": [], "rule_sets": []})
        self.assertIn(f"PASS     lint_009 (DO254-SS4) on {dCase['file']}", sText)
        self.assertIn("Summary: 1 passed, 1 failed, 0 not run", sText)

    def test_design_cases_without_tools(self):
        dManifest = qualify.load("cdc")
        with mock.patch.object(qualify, "load", return_value={"design_cases": dManifest["design_cases"][:1]}):
            with mock.patch.object(qualify, "design_tools", return_value="ERROR: GHDL is not installed"):
                dReport = qualify.run("cdc", 1)
        self.assertEqual({qualify.PASS: 0, qualify.FAIL: 0, qualify.NOT_RUN: 1}, dReport["summary"])
        self.assertEqual("ERROR: GHDL is not installed", dReport["cases"][0]["reason"])

    def test_every_built_in_rule_set_has_a_suite(self):
        from mhsg import rule_set  # pylint: disable=import-outside-toplevel

        for sRuleSet in rule_set.get_built_in_rule_sets():
            with self.subTest(sRuleSet):
                dManifest = qualify.load(sRuleSet)
                for dCase in dManifest.get("cases", []):
                    self.assertTrue(os.path.isfile(os.path.join(qualify.DIRECTORY, dCase["file"])), dCase["file"])

    def test_unknown_rule_set(self):
        with self.assertRaises(ValueError):
            qualify.load("no_such_set")
