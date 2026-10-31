# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_tokens import Rule


class rule_100(Rule):
    """
    This rule checks for a single space before the **open** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       file defaultImage : load_file_type      open read_mode is load_file_name;

    **Fix**

    .. code-block:: vhdl

       file defaultImage : load_file_type open read_mode is load_file_name;
    """

    def __init__(self):
        Rule.__init__(self)
        self.left_token = token.type_mark.name
        self.right_token = token.file_open_information.open_keyword
