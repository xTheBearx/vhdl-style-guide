# -*- coding: utf-8 -*-

import importlib.util
import os
import unittest

sScript = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "real_world_check.py")
oSpec = importlib.util.spec_from_file_location("real_world_check", sScript)
real_world_check = importlib.util.module_from_spec(oSpec)
oSpec.loader.exec_module(real_world_check)

sTraceback = "Traceback (most recent call last):\n  File ...\nKeyError: 1"
sParseError = "Error while processing x.vhd: Unexpected token"


class test_classify(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(real_world_check.classify("", "", "", "a\n", "a\n")[0], real_world_check.OK)

    def test_crash(self):
        self.assertEqual(real_world_check.classify(sTraceback)[0], real_world_check.CRASH)

    def test_parse_error(self):
        self.assertEqual(real_world_check.classify(sParseError)[0], real_world_check.PARSE_ERROR)

    def test_fix_crash(self):
        self.assertEqual(real_world_check.classify("", sTraceback)[0], real_world_check.FIX_CRASH)
        self.assertEqual(real_world_check.classify("", "", sTraceback, "a", "a")[0], real_world_check.FIX_CRASH)

    def test_fix_broke_parse(self):
        self.assertEqual(real_world_check.classify("", "", sParseError, "a", "a")[0], real_world_check.FIX_BROKE_PARSE)

    def test_not_idempotent(self):
        sStatus, sDetails = real_world_check.classify("", "", "", "a\nb\n", "a\n\nb\n")
        self.assertEqual(sStatus, real_world_check.NOT_IDEMPOTENT)
        self.assertIn("+", sDetails)


class test_compare_with_known(unittest.TestCase):
    def test_compare(self):
        lResults = [
            {"file": "ok.vhd", "status": "OK"},
            {"file": "known.vhd", "status": "PARSE_ERROR"},
            {"file": "changed.vhd", "status": "CRASH"},
            {"file": "new.vhd", "status": "NOT_IDEMPOTENT"},
            {"file": "resolved.vhd", "status": "OK"},
        ]
        dKnown = {"known.vhd": "PARSE_ERROR", "changed.vhd": "PARSE_ERROR", "resolved.vhd": "NOT_IDEMPOTENT"}
        lNew, lKnown, lResolved = real_world_check.compare_with_known(lResults, dKnown)
        self.assertEqual([d["file"] for d in lNew], ["changed.vhd", "new.vhd"])
        self.assertEqual([d["file"] for d in lKnown], ["known.vhd"])
        self.assertEqual([d["file"] for d in lResolved], ["resolved.vhd"])


class test_project_list(unittest.TestCase):
    def test_project_list_loads(self):
        lProjects = real_world_check.load_projects(real_world_check.DEFAULT_PROJECTS, [])
        self.assertTrue(lProjects)
        for dProject in lProjects:
            self.assertEqual(len(dProject["commit"]), 40)
