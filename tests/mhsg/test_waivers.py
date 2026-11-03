# -*- coding: utf-8 -*-
"""Waivers: findings accepted with a justification, see mhsg/waivers.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from mhsg import exceptions, waivers

sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sLintFile = os.path.join(sRoot, "tests", "svfile", "lint.sv")


def one(dWaiver):
    return waivers.from_configuration({"waivers": [dWaiver]})[0]


class test_configuration(unittest.TestCase):
    def test_required_keys(self):
        for dWaiver, sMessage in (
            ({"justification": "x"}, "ERROR: waiver 1 needs a rule"),
            ({"rule": "lint_012"}, "ERROR: waiver 1 (rule lint_012) needs a justification"),
            ({"rule": "lint_012", "justification": "  "}, "ERROR: waiver 1 (rule lint_012) needs a justification"),
            (
                {"rule": "lint_012", "justification": "x", "reason": "y"},
                "ERROR: waiver 1 has unknown keys reason; the keys are rule, file, line, message, justification, reviewer",
            ),
            ({"rule": "lint_012", "justification": "x", "line": "top"}, "ERROR: waiver 1 (rule lint_012) has a line that is not a number"),
        ):
            with self.subTest(sMessage):
                with self.assertRaises(exceptions.ConfigurationError) as oContext:
                    waivers.from_configuration({"waivers": [dWaiver]})
                self.assertEqual(sMessage, oContext.exception.message)
        self.assertEqual([], waivers.from_configuration({}))

    def test_matching(self):
        # A rule by identifier, alias or pattern; a file by name, or by path when the pattern has a directory
        self.assertTrue(one({"rule": "sv_lint_unused", "justification": "x"}).matches("sv_lint_005", "a.sv", 3, "m"))
        self.assertTrue(one({"rule": "sv_lint_*", "justification": "x"}).matches("sv_lint_005", "a.sv", 3, "m"))
        oWaiver = one({"rule": "lint_012", "file": "*_sync.vhd", "line": [4, 9], "message": "*sync_r*", "justification": "x"})
        self.assertTrue(oWaiver.matches("lint_012", "rtl/cdc_sync.vhd", 9, "Register sync_r has no reset"))
        self.assertFalse(oWaiver.matches("lint_012", "rtl/cdc_sync.vhd", 5, "Register sync_r has no reset"))
        self.assertFalse(oWaiver.matches("lint_012", "rtl/cdc_sync.vhd", 9, "Register data_r has no reset"))
        self.assertFalse(oWaiver.matches("lint_012", "rtl/top.vhd", 9, "Register sync_r has no reset"))
        oWaiver = one({"rule": "lint_012", "file": "rtl/*.vhd", "justification": "x"})
        self.assertTrue(oWaiver.matches("lint_012", os.path.join("rtl", "top.vhd"), 1, ""))
        self.assertFalse(oWaiver.matches("lint_012", os.path.join("tb", "top.vhd"), 1, ""))


class test_run(unittest.TestCase):
    def run_mhsg(self, lWaivers, lArguments):
        with tempfile.TemporaryDirectory() as sTemporary:
            sCopy = os.path.join(sTemporary, "lint.sv")
            shutil.copy(sLintFile, sCopy)
            sConfiguration = os.path.join(sTemporary, "mhsg.json")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"waivers": lWaivers}, oFile)
            sJson = os.path.join(sTemporary, "out.json")
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sCopy, "-c", sConfiguration, "-js", sJson, "--lint_only", "--rule_set", "none", *lArguments],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            with open(sJson, encoding="utf-8") as oFile:
                dJson = json.load(oFile)
        return oResult, dJson["files"][0]

    def test_waived_findings(self):
        lWaivers = [
            {"rule": "sv_lint_002", "file": "lint.sv", "justification": "The latch is intended", "reviewer": "A. Reviewer"},
            {"rule": "sv_lint_006", "message": "*never matches*", "justification": "Out of date"},
            {"rule": "sv_lint_007", "file": "other.sv", "justification": "Another file"},
        ]
        oResult, dFile = self.run_mhsg(lWaivers, ["-of", "syntastic"])
        self.assertFalse(any("sv_lint_002" in s for s in oResult.stdout.splitlines()))
        self.assertFalse(any(d["rule"] == "sv_lint_002" for d in dFile["violations"]))
        self.assertEqual(
            [
                {
                    "rule": "sv_lint_002",
                    "linenumber": 16,
                    "severity": "Error",
                    "solution": "Latch inferred for 'l_o' because it is not assigned on all control paths",
                    "waiver": 1,
                    "justification": "The latch is intended",
                    "reviewer": "A. Reviewer",
                },
            ],
            dFile["waived"],
        )
        # A waiver that could have matched but did not is reported; one for a file not in the run is not
        self.assertEqual("WARNING: waiver 2 (rule sv_lint_006) matched no finding; it may be out of date\n", oResult.stderr)
        oResult, _ = self.run_mhsg(lWaivers, [])
        self.assertIn("Waived:              1\n  sv_lint_002 line 16: Latch inferred", oResult.stdout)
        self.assertIn("    waiver 1, reviewed by A. Reviewer: The latch is intended\n", oResult.stdout)

    def test_all_waived_passes(self):
        oResult, dFile = self.run_mhsg([{"rule": "sv_lint_*", "justification": "Accepted for the test"}], ["-of", "syntastic"])
        self.assertEqual(0, oResult.returncode, oResult.stdout)
        self.assertEqual([], dFile["violations"])
        self.assertGreater(len(dFile["waived"]), 5)

    def test_invalid_waiver_stops_the_run(self):
        with tempfile.TemporaryDirectory() as sTemporary:
            sConfiguration = os.path.join(sTemporary, "mhsg.json")
            with open(sConfiguration, "w", encoding="utf-8") as oFile:
                json.dump({"waivers": [{"rule": "sv_lint_002"}]}, oFile)
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", sLintFile, "-c", sConfiguration],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(1, oResult.returncode)
        self.assertEqual("ERROR: waiver 1 (rule sv_lint_002) needs a justification\n", oResult.stdout)
