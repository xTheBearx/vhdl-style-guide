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

# Rules of the do254_plus rule set: rule number: [(line, message), ...], each run on its own test input
dPlusExpected = {
    14: [
        (4, "Replace the real type with a fixed point or integer type; synthesis does not support it"),
        (6, "Remove the shared variable; synthesis does not support it"),
        (7, "Remove the access type; synthesis does not support it"),
        (8, "Remove the file declaration; synthesis does not support it"),
        (12, "Remove the after delay; synthesis does not support it"),
        (13, "Remove the transport delay; synthesis does not support it"),
        (13, "Remove the after delay; synthesis does not support it"),
        (17, "Remove the wait statement; synthesis does not support it"),
    ],
    15: [(6, "Code from here is hidden from synthesis; justify the region"), (14, "Code from here is hidden from coverage; justify the region")],
    16: [
        (4, "Give the natural a range, such as range 0 to 15"),
        (12, "Give the natural a range, such as range 0 to 15"),
        (14, "Give the positive a range, such as range 0 to 15"),
    ],
    17: [
        (20, "Assign a defined state in the when others choice of the state machine on state"),
        (17, "Give state one of the attributes fsm_safe_state so synthesis keeps the recovery logic"),
    ],
    18: [(7, "Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the entity"), (20, "Add a requirement tag matching \\bREQ\\s*:\\s*\\S+ to the process")],
    19: [(4, "Replace the buffer port with an out port and an internal signal"), (5, "Use inout ports only on the top level, for device pins")],
    20: [
        (8, "Use rising_edge(clk) or falling_edge(clk) instead of clk'event"),
        (13, "The process uses more than one clock edge (rising edge of clk1, rising edge of clk2); use one process for each"),
    ],
    21: [(5, "Move entity ram to a file of its own; this file already declares fifo"), (2, "Name the file after entity fifo")],
    22: [(11, "Variable count is read before it is written, so it holds its value from the previous clock edge like a register")],
    23: [(3, "Check the generics of entity top with an assertion")],
    24: [(11, "Give state_next a default value at the start of the process")],
    25: [(6, "Use process (all) for the combinational process")],
    26: [(18, "Instantiate fifo with entity work.fifo instead of a component")],
    27: [(18, "Declare the states of fsm_state with an enumerated type instead of std_logic_vector")],
}

# Rules of the do254 rule set added for its planned checks: rule number: [(line, message), ...], each on its own input
dDo254Expected = {
    28: [(11, "Variable sum is read before it is assigned on every path, so it keeps its last value like a latch")],
    29: [
        (5, "Assign one waveform element; synthesis ignores the others and their delays"),
        (10, "Assign one waveform element; synthesis ignores the others and their delays"),
    ],
    30: [(12, "Nesting level 5 is deeper than the limit of 4")],
    31: [(5, "Declare the std_logic_vector with downto, like the other vectors"), (11, "Declare the unsigned with downto, like the other vectors")],
    32: [
        (4, "Give deferred constant c_width its value in the package body of this file, or in the package"),
        (13, "Give deferred constant c_size its value in the package body of this file, or in the package"),
    ],
    33: [(4, "Signal spare is assigned but never read"), (5, "Signal unused is never assigned or read")],
    34: [(10, "Replace 99 by a named constant or generic")],
    35: [(6, 'Replace "0110" by a named constant'), (7, 'Replace x"A5" by a named constant')],
    36: [
        (4, "Function parity_bad can reach its end without returning a value"),
        (22, "Remove the wait statement from procedure pause; synthesis does not support it"),
    ],
    37: [
        (10, "State ERROR of state is never assigned, so the machine never enters it"),
        (19, "State DONE of state assigns no other state, so the machine never leaves it"),
    ],
    38: [(9, "Signal delay_2 inverts delay_1, which inverts trigger: a chain of inverters")],
    39: [
        (13, "The process label busy has the name of a signal; give it a name of its own"),
        (14, "The variable count has the name of a port or generic; give it a name of its own"),
        (17, "The loop parameter clk has the name of a port or generic; give it a name of its own"),
    ],
    40: [(7, "Signal payload connected to port wr_data of u_fifo has another name")],
    41: [(2, "Start the file with a header comment")],
    42: [(2, "Comments are on 14% of the lines; add comments to reach 20%")],
}

# Options set for a rule before it runs
dOptions = {17: {"attributes": ["fsm_safe_state"]}}


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

    def test_plus_violations(self):
        for iRule, lExpected in dPlusExpected.items():
            with self.subTest(rule=iRule):
                oRule = getattr(lint, f"rule_{iRule:03d}")()
                for sOption, oValue in dOptions.get(iRule, {}).items():
                    setattr(oRule, sOption, oValue)
                oFile = read(iRule)
                # rule_021 compares the entity with the file name
                oFile.filename = os.path.join(sTestDir, f"rule_{iRule:03d}_test_input.vhd")
                oRule.analyze(oFile)
                self.assertEqual(lExpected, [(o.get_line_number(), o.get_solution()) for o in oRule.violations])

    def test_do254_violations(self):
        for iRule, lExpected in dDo254Expected.items():
            with self.subTest(rule=iRule):
                oRule = getattr(lint, f"rule_{iRule:03d}")()
                oRule.analyze(read(iRule))
                self.assertEqual(lExpected, [(o.get_line_number(), o.get_solution()) for o in oRule.violations])

    def test_rule_041_required_fields(self):
        # The header has the field Title but not Author
        oRule = lint.rule_041()
        oRule.required_fields = ["Title", "Author"]
        lFile, _ = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_041b_test_input.vhd"))
        oRule.analyze(vhdlFile.vhdlFile(lFile))
        self.assertEqual([(3, "Add the field Author to the file header")], [(o.get_line_number(), o.get_solution()) for o in oRule.violations])

    def test_rule_040_instances(self):
        # The ports of sync, instantiated twice, and of lane, in a for generate, are not checked; leaf is
        # instantiated once, and foo connected to data_i is reported
        oRule = lint.rule_040()
        lFile, _ = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_040b_test_input.vhd"))
        oRule.analyze(vhdlFile.vhdlFile(lFile))
        self.assertEqual(
            [(10, "Signal foo connected to port data_i of u_leaf has another name")],
            [(o.get_line_number(), o.get_solution()) for o in oRule.violations],
        )

    def test_rule_017_without_attributes_option(self):
        oRule = lint.rule_017()
        oRule.analyze(read(17))
        self.assertEqual([20], [o.get_line_number() for o in oRule.violations])

    def test_rule_attributes(self):
        for iRule in list(dExpected) + list(dPlusExpected):
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
