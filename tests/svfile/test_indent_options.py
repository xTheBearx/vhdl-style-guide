# -*- coding: utf-8 -*-
"""The list_indent and begin_style options of sv_indent_001."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sDirectory = os.path.dirname(os.path.abspath(__file__))
sRoot = os.path.dirname(os.path.dirname(sDirectory))


def run(sText, lArguments, sConfiguration=None):
    """Runs mhsg on a copy of a text; returns (the sv_indent_001 lines of its output, the text after)."""
    with tempfile.TemporaryDirectory() as sTemporary:
        sFile = os.path.join(sTemporary, "indent_options.sv")
        with open(sFile, "w", encoding="utf-8") as oFile:
            oFile.write(sText)
        lConfiguration = []
        if sConfiguration:
            sYaml = os.path.join(sTemporary, "mhsg.yaml")
            with open(sYaml, "w", encoding="utf-8") as oFile:
                oFile.write(sConfiguration)
            lConfiguration = ["-c", sYaml]
        oResult = subprocess.run(
            # Every phase when checking; --fix runs them all and does not take -ap
            [sys.executable, "bin/mhsg", "-f", sFile, "-of", "syntastic", *([] if "--fix" in lArguments else ["-ap"]), *lConfiguration, *lArguments],
            cwd=sRoot,
            capture_output=True,
            text=True,
            check=False,
        )
        with open(sFile, encoding="utf-8") as oFile:
            sAfter = oFile.read()
    return [s.split(")", 1)[0].split("(")[-1] for s in oResult.stdout.splitlines() if "sv_indent_001" in s], sAfter


OPTIONS = "rule:\n  sv_indent_001:\n    list_indent: 2\n    begin_style: indented\n"


class test_indent_options(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(sDirectory, "indent_options.sv"), encoding="utf-8") as oFile:
            self.sText = oFile.read()

    def test_options_accept_their_style(self):
        self.assertEqual([], run(self.sText, [], OPTIONS)[0])

    def test_defaults_report_it(self):
        # Ports, parameters and connections one level in; begin at the level of its statement
        self.assertEqual(["2", "4", "5", "6", "7", "11", "12", "16", "17", "18", "19", "20", "21", "22", "23"], run(self.sText, [])[0])

    def test_fix_to_the_options(self):
        # Fixing the default style with the options gives the style of the options
        _, sDefault = run(self.sText, ["--fix"])
        _, sFixed = run(sDefault, ["--fix"], OPTIONS)
        self.assertNotEqual(self.sText, sDefault)
        self.assertEqual(self.sText, sFixed)
