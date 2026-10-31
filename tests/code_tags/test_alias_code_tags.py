# -*- coding: utf-8 -*-
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import process
from tests import utils

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(os.path.dirname(__file__), "alias_code_tag_input.vhd"))


class testAliasCodeTags(unittest.TestCase):
    """
    Code tags accept rule aliases as well as rule identifiers.
    """

    def setUp(self):
        self.assertIsNone(eError)
        self.oFile = vhdlFile.vhdlFile(lFile)

    def test_alias_in_off_on_and_next_line_tags(self):
        # process_016 has the alias process_label_exists. It is disabled by alias, enabled again by alias on line 10,
        # disabled by alias and enabled again by identifier on line 20, and disabled for the next line by alias on line 26.
        oRule = process.rule_016()

        oRule.analyze(self.oFile)
        self.assertEqual(utils.extract_violation_lines_from_violation_object(oRule.violations), [12, 22])

    def test_alias_in_next_line_tag(self):
        # process_018 has the alias process_end_label_exists
        oRule = process.rule_018()

        oRule.analyze(self.oFile)
        self.assertEqual(utils.extract_violation_lines_from_violation_object(oRule.violations), [9, 14, 19, 24])

    def test_local_rule_alias(self):
        # A local rule can define its own alias, which code tags also accept
        oRule = process.rule_016()
        oRule.alias = "my_process_label_rule"
        oFile = vhdlFile.vhdlFile(
            [
                "architecture RTL of ENT is",
                "begin",
                "  -- mhsg_disable_next_line my_process_label_rule",
                "  process (A) is",
                "  begin",
                "  end process;",
                "end architecture RTL;",
            ],
        )

        oRule.analyze(oFile)
        self.assertEqual(oRule.violations, [])
