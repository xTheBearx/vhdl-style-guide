# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import pragma
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_300_test_input.vhd"))
lFile_closing_pragma, eError_closing_pragma = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_300_test_input.closing_pragma.vhd"))

dIndentMap = utils.read_indent_file()


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)
        self.oFile.set_indent_map(dIndentMap)

    def test_default(self):
        oRule = pragma.rule_300()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "pragma")
        self.assertEqual(oRule.identifier, "300")

        lExpected = [2, 17, 19]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_default(self):
        oRule = pragma.rule_300()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_300_test_input.fixed_default.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_zero_indent(self):
        oRule = pragma.rule_300()
        oRule.indent_size = 0

        lExpected = [2, 5, 11, 17, 19]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_zero_indent(self):
        oRule = pragma.rule_300()
        oRule.indent_size = 0

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_300_test_input.fixed_zero_indent.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_closing_pragma_matches_opening_pragma(self):
        # Issue VSG 1520: a closing pragma before begin, when or end was indented to the following statement.
        self.assertIsNone(eError_closing_pragma)
        oFile = vhdlFile.vhdlFile(lFile_closing_pragma)
        oFile.set_indent_map(dIndentMap)
        oRule = pragma.rule_300()

        oRule.analyze(oFile)
        self.assertEqual([], utils.extract_violation_lines_from_violation_object(oRule.violations))
