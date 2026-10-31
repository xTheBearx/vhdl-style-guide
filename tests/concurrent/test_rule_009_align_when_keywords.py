# -*- coding: utf-8 -*-

import unittest

from mhsg import vhdlFile
from mhsg.rules import concurrent, conditional_waveforms
from tests import utils

lFile = [
    "",
    "architecture rtl of e is",
    "begin",
    '  tcp_data_err <= buftx_data_err when data_out_sel = "11" else',
    '                  word3_error when data_out_sel = "10" else',
    "                  '0';",
    "end architecture rtl;",
]

dIndentMap = utils.read_indent_file()


class test_rule(unittest.TestCase):
    # Issue VSG 1586: with align_when_keywords, conditional_waveforms_100 removed the alignment on every fix.
    # The documented configuration allows more than one space before when.
    def test_align_when_keywords_with_conditional_waveforms_100(self):
        oFile = vhdlFile.vhdlFile(lFile)
        oFile.set_indent_map(dIndentMap)

        oAlign = concurrent.rule_009()
        oAlign.align_left = "no"
        oAlign.align_paren = "yes"
        oAlign.align_when_keywords = "yes"
        oAlign.fix(oFile)
        self.assertEqual('                  word3_error    when data_out_sel = "10" else', oFile.get_lines()[5])

        oSpace = conditional_waveforms.rule_100()
        oSpace.number_of_spaces = ">=1"
        oSpace.analyze(oFile)
        self.assertEqual([], oSpace.violations)

        oSpace = conditional_waveforms.rule_100()
        oSpace.analyze(oFile)
        self.assertEqual([5], utils.extract_violation_lines_from_violation_object(oSpace.violations))
