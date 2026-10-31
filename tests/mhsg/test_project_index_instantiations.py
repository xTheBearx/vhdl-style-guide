# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from mhsg import project_index

sCode = """
architecture rtl of top is
begin
  u_named : entity work.named(rtl) port map (clk => clk, data => d(3 downto 0));
  u_positional : entity work.positional port map (clk, f(a, b), q);
  u_mixed : entity lib.Mixed generic map (8) port map (clk, rst => rst);
  u_component : comp port map (a, b);
  -- u_comment : entity work.commented port map (a, b);
  u_string : entity work.with_string port map (s => "a, b");
end architecture rtl;

configuration cfg of top is
  for rtl
    for all : comp use entity work.bound port map (x, y); end for;
  end for;
end configuration cfg;
"""


class test_positional_entity_instantiations(unittest.TestCase):
    def test_get_positional_entity_instantiations(self):
        self.assertEqual({"positional", "mixed", "bound"}, project_index.get_positional_entity_instantiations(sCode))

    def test_collect_from_files(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFile = os.path.join(sDirectory, "top.vhd")
            with open(sFile, "w", encoding="utf-8") as oFile:
                oFile.write(sCode)
            lReturn = project_index.collect_positional_entity_instantiations([sFile, os.path.join(sDirectory, "missing.vhd")])
        self.assertEqual({"positional", "mixed", "bound"}, lReturn)


sDeclarations = """
entity sub is
  generic (G : integer := 4);
  port (q : out std_logic; signal clk, en : in std_logic);  -- port (x : in bit)
end entity sub;

architecture a of top is
  component comp
    port (z : out bit; a : in bit);
  end component;
begin
  u : component comp port map (a => b, z => c);
end architecture a;

entity no_ports is
end entity no_ports;
"""


class test_port_orders(unittest.TestCase):
    def test_get_port_orders(self):
        self.assertEqual(
            [("entity", "sub", ("q", "clk", "en")), ("component", "comp", ("z", "a"))],
            project_index.get_port_orders(sDeclarations),
        )

    def test_collect_port_orders_conflicting_declarations(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            lFiles = []
            for sName, sCode in [("a.vhd", sDeclarations), ("b.vhd", "entity sub is port (clk : in bit); end entity sub;")]:
                lFiles.append(os.path.join(sDirectory, sName))
                with open(lFiles[-1], "w", encoding="utf-8") as oFile:
                    oFile.write(sCode)
            dReturn = project_index.collect_port_orders(lFiles)
        self.assertIsNone(dReturn["entity"]["sub"])
        self.assertEqual(("z", "a"), dReturn["component"]["comp"])
