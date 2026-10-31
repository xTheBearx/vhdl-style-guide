# -*- coding: utf-8 -*-
"""
Fixes each VHDL file in this directory with the default style, compares the
result with the matching .fixed.vhd file, and checks that fixing the result
again changes nothing.
"""

import pathlib
import unittest

from mhsg import rule_list, severity, vhdlFile
from tests import utils

oDirectory = pathlib.Path(__file__).parent
dIndentMap = utils.read_indent_file()


def fix(lLines):
    oFile = vhdlFile.vhdlFile(lLines)
    oFile.set_indent_map(dIndentMap)
    oRuleList = rule_list.rule_list(oFile, severity.create_list({}))
    oRuleList.fix()
    return oFile.get_lines()[1:]


class test_idempotent(unittest.TestCase):
    def test_files(self):
        self.maxDiff = None
        lInputs = sorted(p for p in oDirectory.glob("*.vhd") if not p.name.endswith(".fixed.vhd"))
        self.assertTrue(lInputs)
        for oInput in lInputs:
            with self.subTest(oInput.name):
                lInput, eError = vhdlFile.utils.read_vhdlfile(str(oInput))
                self.assertIsNone(eError)
                lFirst = fix(lInput)
                lExpected = []
                utils.read_file(str(oInput.with_suffix(".fixed.vhd")), lExpected, False)
                self.assertEqual(lExpected, lFirst)
                self.assertEqual(lFirst, fix(lFirst))
