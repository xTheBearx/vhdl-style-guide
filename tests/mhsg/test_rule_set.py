# -*- coding: utf-8 -*-
"""
Tests for rule sets and lint mode.
"""

import os
import subprocess
import tempfile
import unittest

from mhsg import config, exceptions, rule_list, rule_set, severity, vhdlFile
from tests import utils

sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sLintInput = os.path.join(sRoot, "tests", "lint", "rule_009_test_input.vhd")


def rules(sMode="lint", sRuleSet="do254"):
    oSeverities = severity.create_list({})
    oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), oSeverities)
    oConfig = config.config()
    oConfig.severity_list = oSeverities
    oConfig.lint_mode = sMode
    oConfig.rule_set = rule_set.load(sRuleSet)
    rule_set.apply(oRules, oConfig)
    return {o.unique_id: o for o in oRules.rules}


class test_rule_set(unittest.TestCase):
    def test_load(self):
        oRuleSet = rule_set.load("do254")
        self.assertEqual("DO-254", oRuleSet.name)
        self.assertEqual("DO254", oRuleSet.prefix)
        self.assertEqual(49, len(oRuleSet.checks))
        self.assertIsNone(rule_set.load("none"))

    def test_load_unknown(self):
        with self.assertRaises(exceptions.ConfigurationError):
            rule_set.load("unknown_rule_set")

    def test_load_file(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFileName = os.path.join(sDirectory, "mine.yaml")
            with open(sFileName, "w", encoding="utf-8") as oFile:
                oFile.write("name: Mine\nprefix: MY\nchecks:\n  A1:\n    severity: Note\n    rules: [lint_009]\n")
            dRules = rules(sRuleSet=sFileName)
        self.assertEqual(["MY-A1"], dRules["lint_009"].rule_set_labels)
        self.assertEqual("Note", dRules["lint_009"].get_report_severity().name)
        self.assertTrue(dRules["lint_001"].disable)

    def test_unknown_rule_in_rule_set(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFileName = os.path.join(sDirectory, "bad.yaml")
            with open(sFileName, "w", encoding="utf-8") as oFile:
                oFile.write("checks:\n  A1:\n    rules: [lint_999]\n")
            with self.assertRaises(exceptions.ConfigurationError):
                rules(sRuleSet=sFileName)

    def test_do254_labels_and_severities(self):
        dRules = rules()
        self.assertEqual(["DO254-SS4"], dRules["lint_009"].rule_set_labels)
        self.assertFalse(dRules["lint_009"].disable)
        self.assertEqual("Warning", dRules["lint_009"].get_report_severity().name)
        self.assertEqual("Note", dRules["lint_004"].get_report_severity().name)
        self.assertEqual("Error", dRules["lint_003"].get_report_severity().name)
        self.assertEqual(["DO254-DR7"], dRules["whitespace_002"].rule_set_labels)
        self.assertEqual("Warning", dRules["whitespace_002"].get_report_severity().name)
        self.assertEqual("DO254-SS4 (lint_009)", dRules["lint_009"].get_display_id())
        # The rule's own severity, which decides whether --fix fixes it, is not changed
        self.assertEqual("Error", dRules["whitespace_002"].severity.name)

    def test_do254_groups_and_configuration(self):
        dRules = rules()
        # DR6 covers every indent rule
        self.assertIn("DO254-DR6", dRules["process_001"].rule_set_labels)
        # DR13 labels the naming rules without enabling them
        self.assertIn("DO254-DR13", dRules["constant_015"].rule_set_labels)
        self.assertTrue(dRules["constant_015"].disable)
        # DR1 disables the rules that remove labels and enables the ones that require them
        self.assertTrue(dRules["concurrent_005"].disable)
        self.assertFalse(dRules["concurrent_013"].disable)

    def test_lint_and_lint_only(self):
        dLint = rules("lint")
        self.assertFalse(dLint["process_035"].disable)
        dLintOnly = rules("lint_only")
        self.assertTrue(dLintOnly["process_035"].disable)
        self.assertFalse(dLintOnly["lint_001"].disable)
        self.assertFalse(dLintOnly["whitespace_002"].disable)

    def test_no_rule_set(self):
        dRules = rules("lint_only", "none")
        self.assertFalse(dRules["lint_001"].disable)
        self.assertEqual([], dRules["lint_001"].rule_set_labels)
        self.assertTrue(dRules["whitespace_002"].disable)

    def test_lint_rules_off_without_lint_mode(self):
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), severity.create_list({}))
        self.assertTrue(all(o.disable for o in oRules.rules if o.lint))

    def test_configured_severity_replaces_rule_set_severity(self):
        oSeverities = severity.create_list({})
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), oSeverities)
        oConfig = config.config()
        oConfig.severity_list = oSeverities
        oConfig.lint_mode = "lint"
        oConfig.rule_set = rule_set.load("do254")
        rule_set.apply(oRules, oConfig)
        oConfig.dConfig = {"rule": {"whitespace_002": {"severity": "Note"}}}
        oRules.configure(oConfig)
        dRules = {o.unique_id: o for o in oRules.rules}
        self.assertEqual("Note", dRules["whitespace_002"].get_report_severity().name)
        self.assertEqual("Warning", dRules["length_002"].get_report_severity().name)

    def test_most_severe(self):
        self.assertEqual("Error", rule_set.most_severe(["Note", "Error", "Warning"]))
        self.assertEqual("Warning", rule_set.most_severe(["Note", "Warning"]))

    def test_note_severity_is_a_warning(self):
        oSeverities = severity.create_list({})
        self.assertIsNone(oSeverities.get_severity_named("Note"))
        severity.add_note(oSeverities)
        severity.add_note(oSeverities)
        self.assertEqual(["Error", "Warning", "Note"], [o.name for o in oSeverities.get_severities()])
        self.assertEqual(severity.warning_type, oSeverities.get_severity_named("Note").type)


class test_lint_command_line(unittest.TestCase):
    def run_mhsg(self, lArguments):
        oResult = subprocess.run([*utils.mhsg_exec(), "-f", sLintInput, "-of", "syntastic", *lArguments], cwd=sRoot, capture_output=True, text=True, check=False)
        return oResult.stdout.splitlines()

    def test_lint_only_labels(self):
        lOutput = self.run_mhsg(["--lint_only"])
        self.assertIn(f"WARNING: {sLintInput}(9)DO254-SS4 (lint_009) -- Signal out1 is not assigned on every path of the combinational process, which infers a latch", lOutput)
        self.assertFalse(any("process_035" in s for s in lOutput))

    def test_lint_without_rule_set(self):
        lOutput = self.run_mhsg(["--lint_only", "--rule_set", "none"])
        self.assertIn(f"ERROR: {sLintInput}(9)lint_009 -- Signal out1 is not assigned on every path of the combinational process, which infers a latch", lOutput)

    def test_style_run_has_no_lint(self):
        lOutput = self.run_mhsg(["-ap"])
        self.assertFalse(any("lint_" in s for s in lOutput))

    def test_unknown_rule_set(self):
        lOutput = self.run_mhsg(["--lint", "--rule_set", "nothing"])
        self.assertEqual(["ERROR: rule set nothing is not a built in rule set (do254) or a file"], lOutput)


sFixInput = "\n".join(
    [
        "",
        "architecture rtl of fifo is",
        "",
        "begin",
        "",
        "  PROC_A : process (a) is",
        "  begin",
        "",
        "\tb <= a;",
        "        c   <= a;",
        "    if a = '1' then d <= a; end if;",
        "",
        "  end process PROC_A;",
        "",
        "END architecture rtl;",
        "",
    ]
)


class test_lint_fix(unittest.TestCase):
    def fix(self, lArguments):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFileName = os.path.join(sDirectory, "fix.vhd")
            with open(sFileName, "w", encoding="utf-8") as oFile:
                oFile.write(sFixInput)
            oResult = subprocess.run([*utils.mhsg_exec(), "-f", sFileName, "--fix", "-of", "syntastic", *lArguments], cwd=sRoot, capture_output=True, text=True, check=False)
            with open(sFileName, encoding="utf-8") as oFile:
                return oFile.read().splitlines(), oResult.stdout

    def test_lint_fix_fixes_style_like_fix(self):
        lPlain, sPlain = self.fix([])
        lLint, sLint = self.fix(["--lint"])
        self.assertEqual(lPlain, lLint)
        # Tabs (DR7) and indent (DR6) are fixed although the rule set reports them as Warning and Note
        self.assertIn("    b <= a;", lLint)
        self.assertIn("end architecture rtl;", lLint)

    def test_lint_only_fix_fixes_only_the_rule_set_style_rules(self):
        lFixed, sOutput = self.fix(["--lint_only"])
        # Indent and tabs are in the rule set and are fixed
        self.assertIn("    b <= a;", lFixed)
        self.assertIn("    c   <= a;", lFixed)
        # Keyword case and alignment are not in the rule set and are left as they are
        self.assertIn("END architecture rtl;", lFixed)

    def test_lint_checks_run_after_the_fix(self):
        lFixed, sOutput = self.fix(["--lint_only"])
        # DR5 moves the assignment after then to its own line, and the latch is reported on that line of the fixed file
        self.assertEqual("      d <= a;", lFixed[11])
        self.assertIn("(12)DO254-SS4 (lint_009) -- Signal d is not assigned on every path of the combinational process, which infers a latch", sOutput)


class test_rule_set_documentation(unittest.TestCase):
    def test_coverage_table_is_up_to_date(self):
        """docs/do254_coverage.rst is written with rule_set.coverage_table(rule_set.load("do254"))."""
        with open(os.path.join(sRoot, "docs", "do254_coverage.rst"), encoding="utf-8") as oFile:
            self.assertEqual(rule_set.coverage_table(rule_set.load("do254")), oFile.read())

    def test_every_check_has_a_status(self):
        for oCheck in rule_set.load("do254").checks:
            with self.subTest(oCheck.id):
                self.assertIn(oCheck.status, rule_set.STATUS_TEXT)
                self.assertTrue(oCheck.title)
