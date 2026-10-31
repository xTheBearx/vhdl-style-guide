# -*- coding: utf-8 -*-

import unittest

from mhsg import exceptions, vhdlFile
from mhsg.rules import signal

lBroken = [
    "architecture rtl of e is",
    "",
    "  signal A : std_logic;",
    "",
    "begin",
    "",
    "  {off}",
    "  process is",
    "  begin",
    "    a <= b;",
    "  end process",
    "  {on}",
    "",
    "  B <= A;",
    "",
    "end architecture rtl;",
]


def build(sOff, sOn):
    return [sLine.replace("{off}", sOff).replace("{on}", sOn) for sLine in lBroken]


class test_off_region_parsing(unittest.TestCase):
    """
    VSG issue 1590: code the parser cannot handle can be excluded with bare mhsg_off and mhsg_on code tags.
    """

    def test_code_outside_the_region_is_checked(self):
        oFile = vhdlFile.vhdlFile(build("-- mhsg_off", "-- mhsg_on"))
        oRule = signal.rule_004()
        oRule.analyze(oFile)
        self.assertEqual([oViolation.get_line_number() for oViolation in oRule.violations], [3])

    def test_legacy_vsg_tags(self):
        oFile = vhdlFile.vhdlFile(build("-- vsg_off : parser cannot handle this", "-- vsg_on"))
        self.assertEqual(oFile.get_lines()[1:], build("-- vsg_off : parser cannot handle this", "-- vsg_on"))

    def test_fix_leaves_the_region_unchanged(self):
        lLines = build("-- mhsg_off", "-- mhsg_on")
        oFile = vhdlFile.vhdlFile(lLines)
        oRule = signal.rule_004()
        oRule.fix(oFile)
        lActual = oFile.get_lines()[1:]
        self.assertEqual(lActual[6:12], lLines[6:12])
        self.assertEqual(lActual[2], "  signal a : std_logic;")

    def test_rule_specific_tags_do_not_hide_code(self):
        with self.assertRaises(exceptions.ClassifyError):
            vhdlFile.vhdlFile(build("-- mhsg_off signal_004", "-- mhsg_on signal_004"))

    def test_without_tags_the_parse_error_is_reported(self):
        with self.assertRaises(exceptions.ClassifyError):
            vhdlFile.vhdlFile(build("", ""))
