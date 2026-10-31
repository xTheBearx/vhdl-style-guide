# -*- coding: utf-8 -*-

import ast
import glob
import inspect
import unittest

import mhsg.rules


def get_index_names():
    return [sName for sName, oObject in vars(mhsg.rules).items() if inspect.isclass(oObject)]


class test_rules_index(unittest.TestCase):
    """
    VSG issue 1147: mhsg/rules/__init__.py only re-exports base classes for local rules.
    """

    def test_local_rules_can_import_base_classes(self):
        from mhsg.rules import existence_of_tokens_which_should_not_occur, token_case

        self.assertTrue(inspect.isclass(existence_of_tokens_which_should_not_occur))
        self.assertTrue(inspect.isclass(token_case))

    def test_mhsg_imports_base_classes_from_their_modules(self):
        lIndexNames = get_index_names()
        lFound = []
        for sFileName in glob.glob("mhsg/**/*.py", recursive=True):
            if sFileName.replace("\\", "/") == "mhsg/rules/__init__.py":
                continue
            with open(sFileName, encoding="utf-8") as oFile:
                oTree = ast.parse(oFile.read())
            for oNode in ast.walk(oTree):
                if isinstance(oNode, ast.ImportFrom) and oNode.module == "mhsg.rules" and oNode.level == 0:
                    lFound.extend(f"{sFileName}: {oAlias.name}" for oAlias in oNode.names if oAlias.name in lIndexNames)
        self.assertEqual(lFound, [])
