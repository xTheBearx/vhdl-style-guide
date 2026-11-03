# -*- coding: utf-8 -*-
"""A test method defined twice in one class hides the first definition, which then never runs."""

import ast
import collections
import glob
import os
import unittest
import warnings

sTests = os.path.dirname(os.path.abspath(__file__))


class test_no_shadowed_tests(unittest.TestCase):
    def test_method_names_are_unique(self):
        lDuplicates = []
        for sFile in sorted(glob.glob(os.path.join(sTests, "**", "*.py"), recursive=True)):
            with open(sFile, encoding="utf-8") as oFile, warnings.catch_warnings():
                # Some test files have escape sequences Python warns about; they do not matter here
                warnings.simplefilter("ignore", SyntaxWarning)
                oTree = ast.parse(oFile.read())
            for oClass in [o for o in ast.walk(oTree) if isinstance(o, ast.ClassDef)]:
                lNames = [o.name for o in oClass.body if isinstance(o, (ast.FunctionDef, ast.AsyncFunctionDef))]
                for sName, iCount in collections.Counter(lNames).items():
                    if iCount > 1:
                        lDuplicates.append(f"{os.path.relpath(sFile, sTests)}: {oClass.name}.{sName}")
        self.assertEqual([], lDuplicates)
