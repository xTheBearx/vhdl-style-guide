# -*- coding: utf-8 -*-

import json
import os
import re
import subprocess
import unittest
from tempfile import TemporaryDirectory

from mhsg import exceptions, rule_aliases, rule_list, vhdlFile
from tests import utils


def get_rules():
    return rule_list.rule_list(vhdlFile.vhdlFile([""]), None, bAllLanguages=True).rules


class test_rule_aliases(unittest.TestCase):
    def test_every_rule_has_a_valid_unique_alias(self):
        # VSG issue 1529: every rule needs a descriptive alias
        lRules = [oRule for oRule in get_rules() if not oRule.deprecated]
        lRuleIds = {oRule.unique_id for oRule in get_rules()}
        lAliases = []
        for oRule in lRules:
            sAlias = oRule.alias
            self.assertIsNotNone(sAlias, f"{oRule.unique_id} has no alias in mhsg/rule_aliases.yaml")
            self.assertRegex(sAlias, r"^[a-z][a-z0-9_]*$", oRule.unique_id)
            self.assertTrue(sAlias.startswith(oRule.name + "_"), f"alias {sAlias} of {oRule.unique_id} must start with {oRule.name}_")
            self.assertNotIn(sAlias, lRuleIds, f"alias {sAlias} is also a rule identifier")
            lAliases.append(sAlias)
        self.assertEqual(len(lAliases), len(set(lAliases)))

    def test_aliases_file_only_names_existing_rules(self):
        lRuleIds = {oRule.unique_id for oRule in get_rules()}
        for sRuleId in rule_aliases.dAliases:
            self.assertIn(sRuleId, lRuleIds)

    def test_resolve_rule_configuration(self):
        dActual = rule_aliases.resolve_rule_configuration(
            {"global": {"indent_size": 4}, "if_keyword_case": {"case": "upper"}, "if_026": {"case": "upper"}},
            "c.yaml",
        )
        self.assertEqual(dActual, {"global": {"indent_size": 4}, "if_025": {"case": "upper"}, "if_026": {"case": "upper"}})

    def test_resolve_rule_configuration_with_identifier_and_alias(self):
        with self.assertRaises(exceptions.ConfigurationError):
            rule_aliases.resolve_rule_configuration({"if_025": {"case": "upper"}, "if_keyword_case": {"case": "lower"}}, "c.yaml")

    def test_alias_in_configuration_file(self):
        with TemporaryDirectory() as sTmpDir:
            sConfig = os.path.join(sTmpDir, "config.yaml")
            with open(sConfig, "w") as oFile:
                oFile.write("rule:\n  global:\n    disable: true\n  if_keyword_case:\n    disable: false\n    case: upper\n")
            sVhd = os.path.join(sTmpDir, "test.vhd")
            with open(sVhd, "w") as oFile:
                oFile.write("architecture rtl of e is\nbegin\n  process begin\n    if (a = b) then\n    end if;\n  end process;\nend architecture rtl;\n")
            oResult = subprocess.run([*utils.mhsg_exec(), "-f", sVhd, "-c", sConfig, "-of", "syntastic"], capture_output=True, text=True)
        self.assertEqual(oResult.stdout.splitlines(), [f'ERROR: {sVhd}(4)if_025 -- Change "if" to "IF"'])

    def test_rule_configuration_option_accepts_alias(self):
        oResult = subprocess.run([*utils.mhsg_exec(), "-rc", "if_keyword_case"], capture_output=True, text=True)
        dActual = json.loads(oResult.stdout)
        self.assertEqual(list(dActual["rule"].keys()), ["if_025"])
        self.assertEqual(dActual["rule"]["if_025"]["alias"], "if_keyword_case")
