# -*- coding: utf-8 -*-
"""
Tests for the lint rules: each runs on its test input, which holds code that passes and code that fails.
"""

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import lint

sTestDir = os.path.dirname(__file__)

# Rule number: (test input number, [(line, message), ...])
dExpected = {
    1: (1, [(14, "Signal beep is also assigned on line 13 in the same statement region")]),
    2: (
        2,
        [
            (20, "Add sel to the sensitivity list; the process reads it"),
            (20, "Remove c from the sensitivity list; the process does not read it"),
            (29, "Add rst to the sensitivity list"),
            (29, "Remove a from the sensitivity list of the clocked process"),
        ],
    ),
    3: (3, [(25, "Input port in2 of instance u_bad is not connected"), (25, "Input port bus1 of instance u_bad is not connected")]),
    4: (3, [(25, "Output port out1 of instance u_bad is not connected"), (33, "Output port out2 of instance u_positional is not connected")]),
    5: (5, [(8, "Add a when others choice to the case statement")]),
    6: (5, [(13, 'Choice "000" is already covered on line 9')]),
    7: (
        5,
        [
            (15, 'Choice "10X" contains a metavalue and is never reached in hardware'),
            (21, 'Choice "0-Z" contains a metavalue and is never reached in hardware'),
        ],
    ),
    8: (
        8,
        [(11, "Signal gated_in_s is assigned and read in the same combinational process"), (7, "Signal count is assigned from an expression that reads it")],
    ),
    9: (
        9,
        [
            (9, "Signal out1 is not assigned on every path of the combinational process, which infers a latch"),
            (13, "Signal out2 is not assigned on every path of the combinational process, which infers a latch"),
            (22, "Signal out5 is not assigned on every path of the combinational process, which infers a latch"),
        ],
    ),
    10: (10, [(22, "Signal a3 is also driven by process operate_proc on line 15"), (31, "Signal q is also driven by a concurrent assignment on line 29")]),
    11: (
        11,
        [
            (19, "Reset rst_master is active low here but active high on line 9"),
            (19, "Reset rst_master is asynchronous here but synchronous on line 9"),
            (28, "Reset rst_master is asynchronous here but synchronous on line 9"),
        ],
    ),
    12: (
        12,
        [
            (12, "Register out3 is not assigned when reset is active"),
            (20, "Register sync1 has no reset; the process has none"),
            (31, "Register flag is not assigned when rst is active"),
        ],
    ),
    13: (13, [(5, "Remove the initial value of port q"), (12, "Remove the initial value of signal count"), (13, "Remove the initial value of signal a, b")]),
}


def read(iInput):
    lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, f"rule_{iInput:03d}_test_input.vhd"))
    return vhdlFile.vhdlFile(lFile)


class test_lint_rules(unittest.TestCase):
    def test_violations(self):
        for iRule, (iInput, lExpected) in dExpected.items():
            with self.subTest(rule=iRule):
                oRule = getattr(lint, f"rule_{iRule:03d}")()
                oRule.analyze(read(iInput))
                self.assertEqual(lExpected, [(o.get_line_number(), o.get_solution()) for o in oRule.violations])

    def test_rule_attributes(self):
        for iRule in dExpected:
            with self.subTest(rule=iRule):
                oRule = getattr(lint, f"rule_{iRule:03d}")()
                self.assertEqual("lint", oRule.name)
                self.assertEqual(f"{iRule:03d}", oRule.identifier)
                self.assertTrue(oRule.lint)
                self.assertTrue(oRule.disable)
                self.assertFalse(oRule.fixable)
                self.assertIn("lint", oRule.groups)

    def test_fix_changes_nothing(self):
        oFile = read(9)
        lBefore = oFile.get_lines()
        oRule = lint.rule_009()
        oRule.fix(oFile)
        self.assertEqual(lBefore, oFile.get_lines())

    def test_code_tag_disables_rule(self):
        lFile = [
            "",
            "architecture rtl of fifo is",
            "begin",
            "  process (a) is",
            "  begin",
            "    -- mhsg_disable_next_line lint_005",
            "    case a is",
            "      when '0' => y <= '1';",
            "    end case;",
            "    case a is",
            "      when '0' => y <= '1';",
            "    end case;",
            "  end process;",
            "end architecture rtl;",
        ]
        oRule = lint.rule_005()
        oRule.analyze(vhdlFile.vhdlFile(lFile))
        self.assertEqual([10], [o.get_line_number() for o in oRule.violations])
