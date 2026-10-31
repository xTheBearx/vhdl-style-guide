# -*- coding: utf-8 -*-

import os
import unittest

from mhsg import apply_rules

dPort = {"rule": {"port_007": {"disable": True}}}
dEntity = {"rule": {"entity_008": {"case": "upper"}}}

dConfiguration = {
    "file_rules": [
        "tests/mhsg/no_configuration.vhd",
        {"tests/mhsg/entity1.vhd": dPort},
        {"tests/mhsg/entity2.vhd": dPort},
        {os.path.abspath("tests/mhsg/entity1.vhd"): dEntity},
        {"tests/mhsg/empty.vhd": None},
    ],
}


class test_apply_rules(unittest.TestCase):
    def test_relative_path(self):
        self.assertEqual(apply_rules.get_rule_configurations_for_file(dConfiguration, "file_rules", "tests/mhsg/entity2.vhd"), [dPort])

    def test_path_spellings_match(self):
        # VSG issue 593: the same file given as ./x, x or an absolute path must pick up its configuration
        for sFileName in ["./tests/mhsg/entity2.vhd", "tests/./mhsg/entity2.vhd", os.path.abspath("tests/mhsg/entity2.vhd")]:
            self.assertEqual(apply_rules.get_rule_configurations_for_file(dConfiguration, "file_rules", sFileName), [dPort], sFileName)

    def test_all_matching_entries_apply_in_order(self):
        self.assertEqual(apply_rules.get_rule_configurations_for_file(dConfiguration, "file_rules", "tests/mhsg/entity1.vhd"), [dPort, dEntity])

    def test_entries_without_configuration(self):
        self.assertEqual(apply_rules.get_rule_configurations_for_file(dConfiguration, "file_rules", "tests/mhsg/no_configuration.vhd"), [])
        self.assertEqual(apply_rules.get_rule_configurations_for_file(dConfiguration, "file_rules", "tests/mhsg/empty.vhd"), [])

    def test_missing_section(self):
        self.assertEqual(apply_rules.get_rule_configurations_for_file({}, "file_rules", "tests/mhsg/entity1.vhd"), [])
