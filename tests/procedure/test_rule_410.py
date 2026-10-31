# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import procedure
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_410_test_input.vhd"))

dIndentMap = utils.read_indent_file()

lExpected = []
lExpected.append("")
utils.read_file(os.path.join(sTestDir, "rule_410_test_input.fixed.vhd"), lExpected)


lFile_parameter_on_procedure_line, eError_parameter_on_procedure_line = vhdlFile.utils.read_vhdlfile(
    os.path.join(sTestDir, "rule_410_test_input.parameter_on_procedure_line.vhd"),
)

lExpected_parameter_on_procedure_line = []
lExpected_parameter_on_procedure_line.append("")
utils.read_file(os.path.join(sTestDir, "rule_410_test_input.parameter_on_procedure_line.fixed.vhd"), lExpected_parameter_on_procedure_line)


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)
        self.oFile.set_indent_map(dIndentMap)

    def test_rule_410(self):
        oRule = procedure.rule_410()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "procedure")
        self.assertEqual(oRule.identifier, "410")

        lExpected = [18, 19, 21, 22, 39, 40, 42, 61, 62, 64, 83, 84, 86]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_410(self):
        oRule = procedure.rule_410()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_fix_rule_410_parameter_on_procedure_line(self):
        # Issue VSG 1583: with the first parameter on the procedure line, the fix padded the procedure name.
        self.assertIsNone(eError_parameter_on_procedure_line)
        oRule = procedure.rule_410()
        oFile = vhdlFile.vhdlFile(lFile_parameter_on_procedure_line)

        oRule.analyze(oFile)
        self.assertEqual([6, 7], utils.extract_violation_lines_from_violation_object(oRule.violations))

        oRule = procedure.rule_410()
        oRule.fix(oFile)
        self.assertEqual(lExpected_parameter_on_procedure_line, oFile.get_lines())
