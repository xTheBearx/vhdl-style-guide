# -*- coding: utf-8 -*-

from mhsg.rules.whitespace_after_token import Rule
from mhsg.token import external_variable_name as token


class rule_101(Rule):
    """
    This rule checks for a single space after the **variable** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       << variable    dut.fifo.wr_en : std_logic >>

    **Fix**

    .. code-block:: vhdl

       << variable dut.fifo.wr_en : std_logic >>
    """

    def __init__(self):
        Rule.__init__(self, [token.variable_keyword])
