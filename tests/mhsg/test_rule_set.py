# -*- coding: utf-8 -*-
"""
Tests for rule sets and lint mode.
"""

import os
import subprocess
import sys
import tempfile
import unittest

from mhsg import (
    config,
    exceptions,
    project_index,
    rule_list,
    rule_set,
    severity,
    vhdlFile,
)
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

    def test_do254_plus_includes_do254(self):
        oRuleSet = rule_set.load("do254_plus")
        self.assertEqual(["DO-254", "DO-254 plus"], [o.name for o in oRuleSet.all_sets()])
        dRules = rules("lint_only", "do254_plus")
        # Checks of do254 keep their labels; the new checks have their own
        self.assertEqual(["DO254-SS4"], dRules["lint_009"].rule_set_labels)
        self.assertEqual(["DO254PLUS-FSMSAFE"], dRules["lint_017"].rule_set_labels)
        self.assertIn("DO254PLUS-PKG", dRules["use_clause_001"].rule_set_labels)
        self.assertEqual(["std_logic_arith", "std_logic_unsigned", "std_logic_signed", "std_logic_misc"], dRules["use_clause_001"].names)
        self.assertEqual(["u_"], dRules["instantiation_601"].prefixes)
        self.assertFalse(dRules["lint_014"].disable)
        # The do254 set alone does not run the do254_plus checks
        self.assertTrue(rules("lint_only", "do254")["lint_014"].disable)

    def test_extends_cycle(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            for sName, sOther in (("a", "b"), ("b", "a")):
                with open(os.path.join(sDirectory, sName + ".yaml"), "w", encoding="utf-8") as oFile:
                    oFile.write(f"extends: {sOther}.yaml\nchecks: {{}}\n")
            with self.assertRaises(exceptions.ConfigurationError):
                rule_set.load(os.path.join(sDirectory, "a.yaml"))

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
        oResult = subprocess.run(
            [*utils.mhsg_exec(), "-f", sLintInput, "-of", "syntastic", *lArguments],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        return oResult.stdout.splitlines()

    def test_lint_only_labels(self):
        lOutput = self.run_mhsg(["--lint_only"])
        self.assertIn(
            f"WARNING: {sLintInput}(9)DO254-SS4 (lint_009) -- Signal out1 is not assigned on every path of the combinational process, which infers a latch",
            lOutput,
        )
        self.assertFalse(any("process_035" in s for s in lOutput))

    def test_lint_without_rule_set(self):
        lOutput = self.run_mhsg(["--lint_only", "--rule_set", "none"])
        self.assertIn(
            f"ERROR: {sLintInput}(9)lint_009 -- Signal out1 is not assigned on every path of the combinational process, which infers a latch",
            lOutput,
        )

    def test_style_run_has_no_lint(self):
        lOutput = self.run_mhsg(["-ap"])
        self.assertFalse(any("lint_" in s for s in lOutput))

    def test_unknown_rule_set(self):
        lOutput = self.run_mhsg(["--lint", "--rule_set", "nothing"])
        self.assertEqual(["ERROR: rule set nothing is not a built in rule set (cdc, do254, do254_plus, starc) or a file"], lOutput)


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
    ],
)


class test_state_types_in_packages(unittest.TestCase):
    def test_state_machine_typed_in_a_package(self):
        # In lint mode the enumerated types of the other files of the run are known: the machine typed in a package is
        # checked for states never entered or left (lint_037) and for recovery (lint_017), and lint_027 no longer
        # asks for an enumerated type it has
        sDirectory = os.path.join(sRoot, "tests", "lint", "package_fsm")
        lFiles = [os.path.join(sDirectory, s) for s in ("fsm_user.vhd", "fsm_pkg.vhd")]
        oResult = subprocess.run(
            [*utils.mhsg_exec(), "-f", *lFiles, "--rule_set", "do254_plus", "--lint_only", "-of", "syntastic"],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        lFindings = [
            s.replace(sDirectory + os.sep, "") for s in oResult.stdout.splitlines() if any(f"({r})" in s for r in ("lint_017", "lint_027", "lint_037"))
        ]
        self.assertEqual(
            [
                "ERROR: fsm_user.vhd(28)DO254-CP6 (lint_037) -- State FAULT of state_r is never assigned, so the machine never enters it",
                "ERROR: fsm_user.vhd(42)DO254-CP6 (lint_037) -- State DONE of state_r assigns no other state, so the machine never leaves it",
                "ERROR: fsm_user.vhd(46)DO254PLUS-FSMSAFE (lint_017) -- Assign a defined state in the when others choice of the state machine on state_r",
            ],
            lFindings,
        )

    def test_enumerated_types_of_the_run(self):
        # Two files declaring a name with other values leave it out
        self.assertEqual(
            {"state_t": ["IDLE", "RUN"], "bit_t": ["'0'", "'1'"]},
            project_index.get_enumerated_types("type state_t is (IDLE, RUN); type bit_t is ('0', '1'); type a_t is array (0 to 1) of bit;"),
        )
        with tempfile.TemporaryDirectory() as sTemporary:
            lFiles = []
            for sName, sText in (
                ("a.vhd", "type state_t is (IDLE, RUN); type mode_t is (A, B);"),
                ("b.vhd", "type state_t is (OFF, ON); type mode_t is (a, b);"),
            ):
                lFiles.append(os.path.join(sTemporary, sName))
                with open(lFiles[-1], "w", encoding="utf-8") as oFile:
                    oFile.write(sText)
            self.assertEqual({"mode_t": ["A", "B"]}, project_index.collect_enumerated_types(lFiles))


class test_lint_fix(unittest.TestCase):
    def fix(self, lArguments):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFileName = os.path.join(sDirectory, "fix.vhd")
            with open(sFileName, "w", encoding="utf-8") as oFile:
                oFile.write(sFixInput)
            oResult = subprocess.run(
                [*utils.mhsg_exec(), "-f", sFileName, "--fix", "-of", "syntastic", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
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


class test_rule_set_style(unittest.TestCase):
    """The style rules a rule set configures so they agree with its checks (issue 90)."""

    def run_mhsg(self, lFiles, lArguments):
        return subprocess.run([*utils.mhsg_exec(), "-f", *lFiles, "-of", "syntastic", *lArguments], cwd=sRoot, capture_output=True, text=True, check=False)

    def test_fix_converges_with_the_checks(self):
        # Fixed with the default style and do254_plus, the files pass both: no style fix undoes a check, such as
        # removing the comments of a port map (DR11), the labels of calls (DR1), the upper case of generics (NAMES),
        # the entity instantiation (ENTITY) or the line between a requirement tag and its entity (REQ)
        with tempfile.TemporaryDirectory() as sDirectory:
            lFiles = []
            for sFile in ("counter.vhd", "top.vhd"):
                lFiles.append(os.path.join(sDirectory, sFile))
                with open(os.path.join(sRoot, "tests", "mhsg", "rule_set_style", sFile), encoding="utf-8") as oSource, open(
                    lFiles[-1],
                    "w",
                    encoding="utf-8",
                ) as oCopy:
                    oCopy.write(oSource.read())
            for _ in range(2):
                self.run_mhsg(lFiles, ["--rule_set", "do254_plus", "--fix"])
            oResult = self.run_mhsg(lFiles, ["--rule_set", "do254_plus"])
            self.assertEqual("", oResult.stdout)
            self.assertEqual(0, oResult.returncode)
            with open(lFiles[1], encoding="utf-8") as oFile:
                sTop = oFile.read()
            self.assertIn("WIDTH => 8 -- Byte wide", " ".join(sTop.split()))
            self.assertIn("-- REQ: HWR-211\nentity top is", sTop)

    def test_contradictions(self):
        # Options the user sets against a check are reported once; options the rule set also sets are not
        dConfig = {
            "rule": {"case_019": {"disable": False}, "entity_003": {"style": "allow_comment"}},
            "file_list": [{"top.vhd": {"rule": {"generic_map_002": {"case": "lower"}}}}],
        }
        lWarnings = rule_set.contradictions(rule_set.load("do254_plus"), dConfig)
        self.assertEqual(
            [
                "WARNING: the configuration sets disable of case_019 to False, against check DO254-DR1 (Use statement labels), which sets it to True: "
                "case_019 and the rules of the check can report the same code both ways",
                "WARNING: the configuration of top.vhd sets case of generic_map_002 to 'lower', against check DO254PLUS-NAMES (Follow the naming conventions), "
                "which sets it to 'upper': generic_map_002 and the rules of the check can report the same code both ways",
            ],
            lWarnings,
        )
        self.assertEqual([], rule_set.contradictions(None, dConfig))


class test_rule_set_documentation(unittest.TestCase):
    def test_coverage_tables_are_up_to_date(self):
        """docs/<name>_coverage.rst is written with rule_set.coverage_table(rule_set.load(name))."""
        for sName in rule_set.get_built_in_rule_sets():
            with self.subTest(sName), open(os.path.join(sRoot, "docs", sName + "_coverage.rst"), encoding="utf-8") as oFile:
                self.assertEqual(rule_set.coverage_table(rule_set.load(sName)), oFile.read())

    def test_every_check_has_a_status(self):
        for oCheck in rule_set.load("do254").checks + rule_set.load("do254_plus").checks + rule_set.load("starc").checks:
            with self.subTest(oCheck.id):
                self.assertIn(oCheck.status, rule_set.STATUS_TEXT)
                self.assertTrue(oCheck.title)


def run_on_text(sText, sName, lArguments):
    """
    Runs mhsg on a file holding sText with the default configuration, rather than the settings of the VHDL test files;
    returns (exit status, output lines).
    """
    with tempfile.TemporaryDirectory() as sTemporary:
        sFile = os.path.join(sTemporary, sName)
        with open(sFile, "w", encoding="utf-8") as oFile:
            oFile.write(sText)
        oResult = subprocess.run(
            [sys.executable, "bin/mhsg", "-f", sFile, "-of", "syntastic", *lArguments],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
    return oResult.returncode, [s.replace(sFile, sName) for s in oResult.stdout.splitlines()]


class test_starc(unittest.TestCase):
    def test_levels_and_severities(self):
        oRuleSet = rule_set.load("starc")
        self.assertEqual("STARC", oRuleSet.prefix)
        self.assertEqual(613, len(oRuleSet.checks))
        dChecks = {o.id: o for o in oRuleSet.checks}
        self.assertEqual("Error", dChecks["1.1.1.2"].severity)
        self.assertEqual("Warning", dChecks["1.1.1.6"].severity)
        self.assertEqual("Note", dChecks["1.1.1.1"].severity)
        self.assertEqual(["length_001"], dChecks["3.1.4.5"].rules)

    def test_systemverilog(self):
        # A module that follows the other items of the guide: a header with a history, a time unit, ports and comments
        sHeader = "// Module: counter\n// Function: counts\n// Author: A. Designer\n// Date: 2026-11-04\n// History: first version\n"
        sHeader += "`timescale 1ns / 1ps\n"
        sText = sHeader + "module counter (\n  input logic clk_i  // clock\n);\n  logic aa;  // first\n\tlogic bb;  // second\n"
        sText += "  assign aa = " + "b" * 90 + ";\n  assign aa = " + "b" * 110 + ";\nendmodule\n"
        iStatus, lOutput = run_on_text(sText, "counter.sv", ["--rule_set", "starc"])
        self.assertEqual(
            [
                "WARNING: counter.sv(11)STARC-2.7.3.3/STARC-3.1.4.2/STARC-3.1.4.3 (sv_indent_001) -- Use 2 spaces for indent",
                "WARNING: counter.sv(13)STARC-3.1.4.5 (length_001) -- Reduce line to less than 110 characters",
            ],
            lOutput,
        )
        # Notes and warnings do not fail the run
        self.assertEqual(0, iStatus)

    def test_vhdl(self):
        sText = "\nentity e is\nend entity e;\n"
        self.assertEqual((0, []), run_on_text(sText, "e.vhd", ["--rule_set", "starc"]))


class test_rule_sets_and_languages(unittest.TestCase):
    def test_do254_on_systemverilog(self):
        # The VHDL rules of the default rule set are left out for a SystemVerilog file; its own rules ask for a header
        sHeader = "// Module: counter\n// Function: counts\n// Author: mhsg tests\n// Date: 2026-11-08\n"
        self.assertEqual((0, []), run_on_text(sHeader + "module counter;\nendmodule\n", "counter.sv", ["--lint"]))
        self.assertEqual(
            (0, ["WARNING: counter.sv(1)DO254-DR10 (sv_comment_003) -- Start the file with a header comment"]),
            run_on_text("module counter;\nendmodule\n", "counter.sv", ["--lint"]),
        )

    def test_unknown_rule_still_fails(self):
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), None)
        oRuleSet = rule_set.RuleSet({"name": "bad", "checks": {"X": {"rules": ["nothing_001"]}}}, "bad.yaml")
        with self.assertRaises(exceptions.ConfigurationError):
            oRuleSet.apply(oRules, severity.create_list({}))

    def test_rule_set_turns_on_lint(self):
        oResult = subprocess.run(
            [*utils.mhsg_exec(), "-f", sLintInput, "-of", "syntastic", "--rule_set", "do254"],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertTrue(any("DO254-SS4 (lint_009)" in s for s in oResult.stdout.splitlines()))
