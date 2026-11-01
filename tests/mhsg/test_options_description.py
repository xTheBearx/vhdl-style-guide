# -*- coding: utf-8 -*-
"""
Tests for the description of every option, written with --output_options.
"""

import json
import os
import re
import subprocess
import tempfile
import unittest

from mhsg import options_description, rule_list, severity, vhdlFile
from tests import utils

sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sCommittedFile = os.path.join(sRoot, "docs", "mhsg_options.json")

dDescription = options_description.build()


def value_matches(oValue, dDefinition):
    """Returns whether a value fits the type and allowed values of a definition."""
    if oValue is None:
        return dDefinition.get("nullable", False)
    sType = dDefinition["type"]
    if sType == "boolean":
        return isinstance(oValue, bool)
    if sType == "integer":
        return isinstance(oValue, int) and not isinstance(oValue, bool) and dDefinition.get("minimum", oValue) <= oValue <= dDefinition.get("maximum", oValue)
    if sType == "string":
        return isinstance(oValue, str)
    if sType == "enum":
        return oValue in dDefinition["values"]
    if sType == "integer_or_string":
        return (isinstance(oValue, int) and not isinstance(oValue, bool)) or bool(re.fullmatch(r"(>=|<=|>|<)?\d+\+?", str(oValue)))
    if sType == "list":
        return isinstance(oValue, list)
    return False


class test_options_description(unittest.TestCase):
    def test_format(self):
        self.assertEqual("mhsg-options", dDescription["format"])
        self.assertEqual(1, dDescription["format_version"])

    def test_every_rule_option_has_metadata(self):
        dCatalog = options_description.read_catalog()
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), severity.create_list({}))
        lMissing = sorted(
            {(oRule.get_unique_id(), sOption) for oRule in oRules.rules if not oRule.deprecated for sOption in oRule.configuration if sOption not in dCatalog},
        )
        self.assertEqual([], lMissing)

    def test_every_definition_is_complete(self):
        for sId, dDefinition in dDescription["definitions"].items():
            with self.subTest(sId):
                self.assertIn(dDefinition["type"], ("boolean", "integer", "string", "enum", "integer_or_string", "list"))
                self.assertTrue(dDefinition["label"])
                self.assertTrue(dDefinition["description"])
                if dDefinition["type"] == "enum":
                    self.assertTrue(dDefinition["values"])
                if dDefinition["type"] == "list":
                    self.assertIn("item_type", dDefinition)

    def test_every_default_matches_its_definition(self):
        for dRule in dDescription["rules"]:
            for dOption in dRule["options"]:
                with self.subTest(rule=dRule["id"], option=dOption["name"]):
                    dDefinition = dDescription["definitions"][dOption["definition"]]
                    self.assertTrue(value_matches(dOption["default"], dDefinition), f"default {dOption['default']!r} does not match {dDefinition}")

    def test_every_rule_is_listed_once(self):
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), severity.create_list({}))
        lExpected = sorted(o.get_unique_id() for o in oRules.rules if not o.deprecated and not getattr(o, "proposed", False))
        self.assertEqual(lExpected, [d["id"] for d in dDescription["rules"]])

    def test_documentation_pages_exist(self):
        for dRule in dDescription["rules"]:
            with self.subTest(dRule["id"]):
                self.assertTrue(os.path.isfile(os.path.join(sRoot, "docs", dRule["documentation"])))
                if "option_documentation" in dRule:
                    self.assertTrue(os.path.isfile(os.path.join(sRoot, "docs", dRule["option_documentation"])))

    def test_settings_defaults_match(self):
        for dSetting in dDescription["settings"]:
            with self.subTest(".".join(dSetting["path"])):
                self.assertTrue(dSetting["label"])
                self.assertTrue(dSetting["description"])
                if dSetting["type"] in ("boolean", "list", "enum", "string", "integer"):
                    self.assertTrue(value_matches(dSetting["default"], dSetting))

    def test_committed_file_is_up_to_date(self):
        """
        docs/mhsg_options.json is written with: python -c "from mhsg import options_description; options_description.write('docs/mhsg_options.json')"
        """
        with open(sCommittedFile, encoding="utf-8") as oFile:
            dCommitted = json.load(oFile)
        dCurrent = json.loads(options_description.to_json(dDescription))
        # The version changes with every commit
        del dCommitted["mhsg_version"]
        del dCurrent["mhsg_version"]
        self.assertTrue(dCommitted == dCurrent, "docs/mhsg_options.json is out of date, regenerate it as described in this test")

    def test_command_line_option_with_local_rules(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFileName = os.path.join(sDirectory, "options.json")
            subprocess.check_output([*utils.mhsg_exec(), "--output_options", sFileName, "-lr", "tests/mhsg/local_rules"], cwd=sRoot)
            with open(sFileName, encoding="utf-8") as oFile:
                dWritten = json.load(oFile)
        dRule = {d["id"]: d for d in dWritten["rules"]}["localized_001"]
        self.assertIsNone(dRule["documentation"])
        self.assertEqual(
            ["disable", "fixable", "indent_size", "indent_style", "phase", "severity", "user_error_message"],
            sorted(d["name"] for d in dRule["options"]),
        )
        self.assertEqual(len(dDescription["rules"]) + 1, len(dWritten["rules"]))

    def test_option_of_local_rule_without_metadata(self):
        dDefinitions = {}
        self.assertEqual("max_ports:localized_002", options_description.add_definition("max_ports", None, "localized_002", 20, {}, dDefinitions))
        self.assertEqual({"type": "integer", "label": "Max ports", "description": ""}, dDefinitions["max_ports:localized_002"])
