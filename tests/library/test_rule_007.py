# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import config, vhdlFile
from mhsg.rules import library
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_007_test_input.vhd"))


class test_rule(unittest.TestCase):
    def setUp(self):
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.assertIsNone(eError)

    def test_rule_007_no_blank_line(self):
        oRule = library.rule_007()
        oRule.style = "no_blank_line"

        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "library")
        self.assertEqual(oRule.identifier, "007")

        lExpected = [3, 12, 17, 23, 25, 28, 34, 43, 52, 61, 70, 79, 88, 97, 107]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_007_no_blank_line(self):
        oRule = library.rule_007()
        oRule.style = "no_blank_line"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_007_test_input.fixed_no_blank_line.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_007_no_blank_line_unless_different_library(self):
        oRule = library.rule_007()
        oRule.style = "no_blank_line_unless_different_library"

        lExpected = [12, 17, 23, 28, 107, 123, 125]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_007_no_blank_line_unless_different_library(self):
        oRule = library.rule_007()
        oRule.style = "no_blank_line_unless_different_library"

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        lExpected = []
        lExpected.append("")
        utils.read_file(os.path.join(sTestDir, "rule_007_test_input.fixed_no_blank_line_unless_different_library.vhd"), lExpected)

        self.assertEqual(lExpected, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_rule_007_accepts_library_style(self):
        oConfig = config.config()
        oConfig.dConfig = {"rule": {"library_007": {"style": "no_blank_line_unless_different_library"}}}

        oRule = library.rule_007()
        self.assertEqual([], oRule.configure(oConfig))
