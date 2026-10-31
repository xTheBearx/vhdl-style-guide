# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import constant, signal, variable

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rename_local_input.vhd"))


def fix(oRule):
    oFile = vhdlFile.vhdlFile(lFile)
    oRule.fixable = True
    oRule.fix(oFile)
    return oFile.get_lines()[1:]


class test_rename_local(unittest.TestCase):
    """
    VSG issue 558: prefix and suffix rules can rename local declarations and their references.
    """

    def setUp(self):
        self.assertIsNone(eError)

    def test_not_fixed_unless_fixable_is_enabled(self):
        oFile = vhdlFile.vhdlFile(lFile)
        oRule = signal.rule_008()
        oRule.fix(oFile)
        self.assertEqual(oFile.get_lines()[1:], lFile)

    def test_signal_prefix(self):
        lActual = fix(signal.rule_008())
        # Declarations and references in the architecture are renamed
        self.assertEqual(lActual[20], "  signal   s_valid       : std_logic;")
        self.assertEqual(lActual[21], "  signal   s_rec         : t_rec;")
        self.assertEqual(lActual[34], "  s_valid <= data;")
        # Record element choices and selected element names keep the element name
        self.assertEqual(lActual[35], "  s_rec   <= (valid => s_valid);")
        self.assertEqual(lActual[36], "  s_rec.valid <= s_valid;")
        # The record element declaration and port map formals are not renamed
        self.assertEqual(lActual[16], "    valid : std_logic;")
        self.assertEqual(lActual[40], "      valid => s_valid")
        # A variable of the same name in the function hides the signal
        self.assertEqual(lActual[26], "    variable valid : integer;")
        self.assertEqual(lActual[28], "    valid := x;")
        # count is not renamed, because s_count already exists
        self.assertEqual(lActual[22], "  signal   count       : integer;")
        # The port is not local, so it is not renamed
        self.assertEqual(lActual[9], "    data : in std_logic")

    def test_variable_prefix(self):
        lActual = fix(variable.rule_012())
        self.assertEqual(lActual[26], "    variable v_valid : integer;")
        self.assertEqual(lActual[29], "    return v_valid;")
        self.assertEqual(lActual[46], "    tmp := const_depth;".replace("tmp", "v_tmp"))
        # The signal of the same name outside the function is not renamed
        self.assertEqual(lActual[34], "  valid <= data;")

    def test_constant_prefix_with_remove_prefixes(self):
        oRule = constant.rule_015()
        oRule.remove_prefixes = ["const_"]
        lActual = fix(oRule)
        self.assertEqual(lActual[19], "  constant c_depth : integer := 16;")
        self.assertEqual(lActual[46], "    tmp := c_depth;")
        # The package constant can be seen by other files, so it is not renamed
        self.assertEqual(lActual[3], "  constant width : integer := 8;")

    def test_suffix(self):
        oRule = signal.rule_600()
        lActual = fix(oRule)
        self.assertEqual(lActual[20], "  signal   valid_s       : std_logic;")
        self.assertEqual(lActual[34], "  valid_s <= data;")
