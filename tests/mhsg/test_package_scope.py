# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import config, rule_list, vhdlFile
from mhsg.rules import package_scope

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(os.path.dirname(__file__), "..", "constant", "rule_601_test_input.vhd"))


def get_rules(dConfig):
    oFile = vhdlFile.vhdlFile(lFile)
    oRules = rule_list.rule_list(oFile, None)
    oConfig = config.config()
    oConfig.dConfig = dConfig
    oRules.configure(oConfig)
    dRules = {oRule.unique_id: oRule for oRule in oRules.rules}
    return oFile, dRules


def get_violation_lines(oRule, oFile):
    oRule.analyze(oFile)
    return [oViolation.get_line_number() for oViolation in oRule.violations]


class test_package_scope(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(eError)

    def test_general_rule_checks_everything_by_default(self):
        oFile, dRules = get_rules({"rule": {"constant_015": {"disable": False}}})

        self.assertEqual(dRules["constant_015"].package_scope, package_scope.ALL)
        self.assertEqual(get_violation_lines(dRules["constant_015"], oFile), [5, 11, 14, 23])

    def test_general_rule_skips_packages_when_package_rule_enabled(self):
        # VSG issue 690: names in packages are checked by constant_601 instead of constant_015
        oFile, dRules = get_rules({"rule": {"constant_015": {"disable": False}, "constant_601": {"disable": False, "prefixes": ["pc_"]}}})

        self.assertEqual(dRules["constant_015"].package_scope, package_scope.EXCLUDE_PACKAGES)
        self.assertEqual(get_violation_lines(dRules["constant_015"], oFile), [14, 23])
        self.assertEqual(get_violation_lines(dRules["constant_601"], oFile), [4, 5, 11])

    def test_every_package_rule_names_an_existing_general_rule(self):
        _, dRules = get_rules({"rule": {}})
        for oRule in dRules.values():
            sGeneralRule = getattr(oRule, "general_rule", None)
            if sGeneralRule is not None:
                self.assertIn(sGeneralRule, dRules, oRule.unique_id)
                self.assertEqual(dRules[sGeneralRule].package_scope, package_scope.ALL)
