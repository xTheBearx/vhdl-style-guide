# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import procedure_call
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_400_test_input.smart_tabs.vhd"))

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
