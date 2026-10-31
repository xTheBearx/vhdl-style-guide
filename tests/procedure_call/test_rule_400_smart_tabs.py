# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import procedure_call
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_400_test_input.smart_tabs.vhd"))
lFile_misaligned, eError_misaligned = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_400_test_input.smart_tabs_misaligned.vhd"))

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_400_test_input.smart_tabs.vhd"), lExpected)

dIndentMap = utils.read_indent_file()


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)
        self.oFile.set_indent_map(dIndentMap)

    def test_rule_400_smart_tabs(self):
        # Issue VSG 1483: parameters indented with tabs were reported as needing one tab and spaces.
        oRule = procedure_call.rule_400()
        oRule.indent_style = "smart_tabs"
        oRule.align_left = "yes"
        oRule.align_paren = "no"

        oRule.analyze(self.oFile)
        self.assertEqual([], utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_400_smart_tabs(self):
        # The parameters are indented, not aligned, so whole indent levels use tabs.
        self.assertIsNone(eError_misaligned)
        oFile = vhdlFile.vhdlFile(lFile_misaligned)
        oFile.set_indent_map(dIndentMap)
        oRule = procedure_call.rule_400()
        oRule.indent_style = "smart_tabs"
        oRule.align_left = "yes"
        oRule.align_paren = "no"

        oRule.analyze(oFile)
        self.assertEqual([15, 16, 17, 18], utils.extract_violation_lines_from_violation_object(oRule.violations))

        oRule = procedure_call.rule_400()
        oRule.indent_style = "smart_tabs"
        oRule.align_left = "yes"
        oRule.align_paren = "no"
        oRule.fix(oFile)
        self.assertEqual(lExpected, oFile.get_lines())
