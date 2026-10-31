# -*- coding: utf-8 -*-

import unittest

from mhsg import vhdlFile
from mhsg.rules import architecture, constant, signal

lCode = [
    "library ieee;",
    "  use ieee.std_logic_1164.all;",
    "",
    "entity e is",
    "  generic (",
    "    g_width : natural := 8",
    "  );",
    "  port (",
    "    DEBUG : out std_logic_vector(3 downto 0)",
    "  );",
    "end entity e;",
    "",
    "architecture rtl of e is",
    "",
    "  signal data : std_logic;",
    "",
    "  function f (x : integer) return integer is",
    "    variable DATA : integer;",
    "  begin",
    "    DATA := x;",
    "    return DATA;",
    "  end function f;",
    "",
    "begin",
    "",
    '  assert G_WIDTH >= 8 report "too narrow" severity failure;',
    "",
    "  gen : if G_WIDTH > 4 generate",
    "    constant c_size : integer := 2;",
    "  begin",
    "    debug(0) <= DATA;",
    "    debug(1) <= '0' when C_SIZE > 1 else '1';",
    "  end generate gen;",
    "",
    "  u1 : entity work.sub",
    "    generic map (",
    "      G_WIDTH => g_width",
    "    );",
    "",
    "end architecture rtl;",
]


def lines_of(oRule):
    oRule.analyze(vhdlFile.vhdlFile(lCode))
    return [(oViolation.get_line_number(), oViolation.sSolution) for oViolation in oRule.violations]


class test_declaration_scoping(unittest.TestCase):
    """
    The consistency rules use the declaration list to decide what a name refers to.
    """

    def test_variable_hides_signal(self):
        # DATA in the function is the variable, so only the use in the generate is the signal
        self.assertEqual(lines_of(signal.rule_014()), [(31, "Change DATA to data")])

    def test_generics_in_concurrent_assertions_and_generate_conditions(self):
        lActual = lines_of(architecture.rule_600())
        self.assertIn((26, "Generic case mismatch:  Change G_WIDTH to g_width"), lActual)
        self.assertIn((28, "Generic case mismatch:  Change G_WIDTH to g_width"), lActual)
        # The formal of the generic map belongs to the instantiated entity
        self.assertNotIn(37, [iLine for iLine, _ in lActual])

    def test_ports_in_indexed_targets(self):
        lActual = lines_of(architecture.rule_601())
        self.assertEqual([iLine for iLine, _ in lActual], [31, 32])

    def test_constant_in_generate(self):
        self.assertEqual(lines_of(constant.rule_013()), [(32, "Change C_SIZE to c_size")])

    def test_context_clause_applies_to_next_unit_only(self):
        lFile = [
            "package pkg is",
            "  constant c_width : integer := 8;",
            "end package pkg;",
            "",
            "use work.pkg.all;",
            "entity e is",
            "end entity e;",
            "",
            "architecture rtl of e is",
            "  signal s : integer := C_WIDTH;",
            "begin",
            "end architecture rtl;",
            "",
            "package other is",
            "  constant c_other : integer := C_WIDTH;",
            "end package other;",
        ]
        oRule = constant.rule_013()
        oRule.analyze(vhdlFile.vhdlFile(lFile))
        # The architecture of e sees pkg through the use clause of e, package other does not
        self.assertEqual([oViolation.get_line_number() for oViolation in oRule.violations], [10])
