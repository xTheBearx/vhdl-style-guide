# -*- coding: utf-8 -*-
import os
import unittest

from mhsg import vhdlFile
from mhsg.rules import signal
from tests import utils

lFile, eError = vhdlFile.utils.read_vhdlfile(os.path.join(os.path.dirname(__file__), "block_comment_code_tag_input.vhd"))
oFile = vhdlFile.vhdlFile(lFile)


class test_block_comment_code_tags(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(eError)

    def test_tags_in_delimited_comments(self):
        # A delimited comment on one line is a code tag, as a line comment is; one over several lines is not
        oRule = signal.rule_002()
        oRule.analyze(oFile)
        self.assertEqual([8, 14], utils.extract_violation_lines_from_violation_object(oRule.violations))
