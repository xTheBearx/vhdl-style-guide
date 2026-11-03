# -*- coding: utf-8 -*-
"""The summaries of VHDL files design analysis keeps in a cache, see mhsg/design/source_summary.py."""

import os
import tempfile
import unittest
from unittest import mock

from mhsg.design import source_summary

sCode = """
entity e is
  port (clk : in std_logic; d : in std_logic; q : out std_logic);
end entity e;

architecture rtl of e is
  signal r : std_logic;
begin

  process (clk) is
  begin
    if rising_edge(clk) then
      r <= d;
      q <= r;
    end if;
  end process;

end architecture rtl;
"""


class test_source_summary(unittest.TestCase):
    def test_summary_and_cache(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFile = os.path.join(sDirectory, "e.vhd")
            with open(sFile, "w", encoding="utf-8") as oFile:
                oFile.write(sCode)
            with mock.patch.dict(os.environ, {"MHSG_CACHE_DIRECTORY": os.path.join(sDirectory, "cache")}):
                lArchitectures = source_summary.load(sFile)
                self.assertEqual(1, len(lArchitectures))
                oProcess = lArchitectures[0].processes[0]
                self.assertEqual((10, 16, True, [("r", 13), ("q", 14)]), (oProcess.line, oProcess.end_line, oProcess.clocked, oProcess.assignments))
                self.assertEqual(10, lArchitectures[0].first_statement)
                # The second load reads the cache, not the file's parse; a changed file is parsed again
                with mock.patch.object(source_summary, "summarize", wraps=source_summary.summarize) as oSummarize:
                    lCached = source_summary.load(sFile)
                    self.assertEqual(0, oSummarize.call_count)
                    with open(sFile, "a", encoding="utf-8") as oFile:
                        oFile.write("\n")
                    source_summary.load(sFile)
                    self.assertEqual(1, oSummarize.call_count)
                self.assertEqual(oProcess.assignments, lCached[0].processes[0].assignments)

    def test_cache_off(self):
        with mock.patch.dict(os.environ, {"MHSG_CACHE_DIRECTORY": ""}):
            self.assertIsNone(source_summary.cache_directory())
