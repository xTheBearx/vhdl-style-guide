# -*- coding: utf-8 -*-
"""Lint after --fix: the files are fixed first and compiled together again, see fix_before_lint in __main__.py."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix_lint")
sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class test_fix_lint(unittest.TestCase):
    def test_fixed_file_is_linted_with_the_run(self):
        # z_o is reported as undriven only when fl_sub.sv, which fl_top.sv instantiates, is compiled with it; the
        # fix changes fl_top.sv, which would otherwise be linted on its own
        with tempfile.TemporaryDirectory() as sTemporary:
            lFiles = []
            for sFile in ("fl_top.sv", "fl_sub.sv"):
                shutil.copy(os.path.join(sDirectory, sFile), sTemporary)
                lFiles.append(os.path.join(sTemporary, sFile))
            oResult = subprocess.run(
                [sys.executable, "bin/mhsg", "-f", *lFiles, "--fix", "--backup", "--lint", "--rule_set", "none", "-of", "syntastic"],
                cwd=sRoot,
                capture_output=True,
                text=True,
                check=False,
            )
            with open(lFiles[0], encoding="utf-8") as oFile:
                sFixed = oFile.read()
            with open(lFiles[0] + ".bak", encoding="utf-8") as oFile:
                sBackup = oFile.read()
        self.assertEqual([f"ERROR: {lFiles[0]}(4)sv_lint_010 -- Undriven output port 'z_o'"], oResult.stdout.splitlines())
        self.assertIn("\n    fl_sub u_sub (\n        .a_i(a_i),\n", sFixed)
        # The backup holds the file as it was before the fixes
        with open(os.path.join(sDirectory, "fl_top.sv"), encoding="utf-8") as oFile:
            self.assertEqual(oFile.read(), sBackup)
