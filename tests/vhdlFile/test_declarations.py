# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import vhdlFile

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(os.path.dirname(__file__), "declarations_input.vhd"))


def index_of(oFile, sValue, iOccurrence=0):
    lIndexes = [iIndex for iIndex, oToken in enumerate(oFile.lAllObjects) if oToken.get_value() == sValue]
    return lIndexes[iOccurrence]


class test_declarations(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(eError)
        self.oFile = vhdlFile.vhdlFile(lFile)
        self.oDeclarations = self.oFile.get_declarations()

    def find_kinds(self, sName, iIndex):
        return [(oDeclaration.kind, oDeclaration.scope.kind) for oDeclaration in self.oDeclarations.find(sName, iIndex)]

    def test_scopes(self):
        lActual = [(oScope.kind, oScope.name) for oScope in self.oDeclarations.scopes]
        lExpected = [
            ("design_file", None),
            ("package", "pkg"),
            ("package_body", "pkg"),
            ("entity", "e"),
            ("architecture", "rtl"),
            ("record", None),
            ("subprogram", "f"),
            ("process", None),
            ("loop", None),
            ("generate", None),
        ]
        self.assertEqual(lActual, lExpected)

    def test_declaration_kinds(self):
        dActual = {oDeclaration.name: oDeclaration.kind for oDeclaration in self.oDeclarations.declarations}
        self.assertEqual(dActual["t_state"], "type")
        self.assertEqual(dActual["IDLE"], "enumeration_literal")
        self.assertEqual(dActual["g_depth"], "generic")
        self.assertEqual(dActual["clk"], "port")
        self.assertEqual(dActual["x"], "parameter")
        self.assertEqual(dActual["f"], "function")
        self.assertEqual(dActual["proc"], "label")
        self.assertEqual(dActual["i"], "loop_parameter")
        self.assertEqual(dActual["j"], "loop_parameter")
        self.assertEqual(dActual["rtl"], "architecture")

    def test_architecture_sees_its_entity(self):
        self.assertEqual(self.find_kinds("clk", index_of(self.oFile, "clk", 1)), [("port", "entity")])
        self.assertEqual(self.find_kinds("g_depth", index_of(self.oFile, "g_depth", 1)), [("generic", "entity")])

    def test_package_body_sees_its_package(self):
        self.assertEqual(self.find_kinds("c_width", index_of(self.oFile, "c_width", 1)), [("constant", "package")])

    def test_packages_in_the_file_are_visible(self):
        self.assertEqual(self.find_kinds("t_state", index_of(self.oFile, "t_state", 1)), [("type", "package")])

    def test_inner_declaration_hides_outer(self):
        # valid inside the function is the variable, outside it is the signal
        self.assertEqual(self.find_kinds("valid", index_of(self.oFile, "valid", 3)), [("variable", "subprogram")])
        self.assertEqual(self.find_kinds("valid", index_of(self.oFile, "valid", 5)), [("signal", "architecture")])

    def test_record_elements_are_not_visible_by_name(self):
        self.assertEqual(self.find_kinds("valid", index_of(self.oFile, "valid", 5)), [("signal", "architecture")])

    def test_loop_and_generate_parameters(self):
        self.assertEqual(self.find_kinds("i", index_of(self.oFile, "i", 1)), [("loop_parameter", "loop")])
        self.assertEqual(self.find_kinds("s_gen", index_of(self.oFile, "s_gen", 1)), [("signal", "generate")])
        # Outside the loop, the parameter is not visible
        self.assertEqual(self.find_kinds("i", index_of(self.oFile, "s_gen", 1)), [])

    def test_unknown_name(self):
        self.assertEqual(self.oDeclarations.find("unknown", 0), [])
