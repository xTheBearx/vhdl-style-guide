# -*- coding: utf-8 -*-

import copy
import importlib
import os
import unittest

from mhsg import project_index, vhdlFile
from mhsg.rules import subtype, type_definition, type_mark
from tests import utils

sTestDir = os.path.dirname(__file__)

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(sTestDir, "rule_501_test_input.vhd"))

lExpected_lower = []
lExpected_lower.append("")
utils.read_file(os.path.join(sTestDir, "rule_501_test_input.fixed_lower.vhd"), lExpected_lower)


def configuration_with_project_types(lTypeNames):
    # A type declared in another file of the run
    oConfig = copy.copy(importlib.import_module("mhsg.vhdlFile.vhdlFile").default_conf)
    oConfig.project_type_names = set(lTypeNames)
    return oConfig


class test_rule(unittest.TestCase):
    """
    VSG issue 1416: the case of type conversions such as STD_LOGIC_VECTOR(x).
    """

    def setUp(self):
        self.assertIsNone(eError)
        self.oFile = vhdlFile.vhdlFile(lFile, configuration=configuration_with_project_types(["t_project"]))

    def test_rule_501_lower(self):
        oRule = type_mark.rule_501()
        self.assertTrue(oRule)
        self.assertEqual(oRule.name, "type_mark")
        self.assertEqual(oRule.identifier, "501")
        self.assertTrue(oRule.disable)

        lExpected = [17, 18, 18, 20, 20, 23, 24]

        oRule.analyze(self.oFile)
        self.assertEqual(lExpected, utils.extract_violation_lines_from_violation_object(oRule.violations))

    def test_fix_rule_501_lower(self):
        oRule = type_mark.rule_501()

        oRule.fix(self.oFile)

        lActual = self.oFile.get_lines()

        self.assertEqual(lExpected_lower, lActual)

        oRule.analyze(self.oFile)
        self.assertEqual(oRule.violations, [])

    def test_types_in_other_files_need_the_project_index(self):
        oRule = type_mark.rule_501()
        oFile = vhdlFile.vhdlFile(lFile)
        oRule.analyze(oFile)
        self.assertNotIn(24, utils.extract_violation_lines_from_violation_object(oRule.violations))


class test_conversions_of_types_declared_in_the_file(unittest.TestCase):
    """
    Type conversions to types declared in the file keep the case of the declaration.
    """

    lFile = [
        "architecture a of b is",
        "  type t_Word is array (0 to 3) of std_logic;",
        "  subtype my_type is std_logic_vector(7 downto 0);",
        "begin",
        "  x <= MY_TYPE(y);",
        "  w <= T_WORD(v);",
        "  u1 : entity work.sub port map (a => My_Type(y));",
        "end architecture a;",
    ]

    def test_type(self):
        oRule = type_definition.rule_014()
        oRule.analyze(vhdlFile.vhdlFile(self.lFile))
        self.assertEqual([oViolation.sSolution for oViolation in oRule.violations], ["Change T_WORD to t_Word"])

    def test_subtype(self):
        oRule = subtype.rule_002()
        oRule.analyze(vhdlFile.vhdlFile(self.lFile))
        self.assertEqual([oViolation.sSolution for oViolation in oRule.violations], ["Change MY_TYPE to my_type", "Change My_Type to my_type"])


class test_project_index(unittest.TestCase):
    def test_type_names(self):
        sText = """
        -- type t_comment is (a, b);
        package pkg is
          type T_State is (idle, run);
          subtype t_byte is std_logic_vector(7 downto 0);
          constant c_text : string := "type t_string is";
        end package pkg;
        """
        self.assertEqual(project_index.get_type_names(sText), {"t_state", "t_byte"})

    def test_collect_type_names_skips_missing_files(self):
        self.assertEqual(project_index.collect_type_names(["missing_file.vhd"]), set())
