# -*- coding: utf-8 -*-

import unittest

from mhsg import exceptions, vhdlFile


def get_error(lLines, sFilename="test.vhd"):
    try:
        vhdlFile.vhdlFile(lLines, sFilename=sFilename)
    except exceptions.ClassifyError as e:
        return e.message
    return None


class test_malformed_vhdl(unittest.TestCase):
    """
    VSG issue 669: malformed VHDL is reported as a syntax error instead of a Python traceback.
    """

    def test_file_ending_inside_a_statement(self):
        sMessage = get_error(["architecture rtl of e is", "begin", "  process", "  begin", "    if (a = b) then", "      c <= d;"])
        self.assertIn("Unexpected end of file while parsing if_statement", sMessage)
        self.assertIn("in file test.vhd", sMessage)

    def test_file_ending_inside_a_use_clause(self):
        sMessage = get_error(["library ieee;", "use"])
        self.assertIn("Unexpected end of file while parsing use_clause", sMessage)

    def test_file_ending_inside_parentheses(self):
        sMessage = get_error(["architecture rtl of e is", "  type t is array(natural range <>) of std_logic_vector(7 downto"])
        self.assertIn("Unexpected end of file", sMessage)

    def test_unmatched_closing_parenthesis(self):
        sMessage = get_error(["architecture rtl of e is", "begin", "  a <= b);", "end architecture rtl;"])
        self.assertIn("Closing parenthesis without an opening parenthesis @ Line 3", sMessage)

    def test_missing_keyword_at_end_of_file(self):
        sMessage = get_error(
            [
                "architecture rtl of e is",
                "begin",
                "  process",
                "  begin",
                "    if a = b",
                "      c <= d;",
                "    end if;",
                "  end process;",
                "end architecture rtl;",
            ],
        )
        self.assertIn("Expecting : then", sMessage)
        self.assertIn("Found     : end of file", sMessage)

    def test_filename_in_message(self):
        sMessage = get_error(["entity e is", "  port (", "    a : in std_logic", "    b : out std_logic", "  );", "end entity e;"], "my_file.vhd")
        self.assertIn("in file my_file.vhd", sMessage)
