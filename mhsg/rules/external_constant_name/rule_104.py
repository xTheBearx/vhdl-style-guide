# -*- coding: utf-8 -*-

from mhsg.rules.whitespace_before_token import Rule
from mhsg.token import external_constant_name as token


class rule_104(Rule):
    """
    This rule checks for a single space before the double greater than.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       << constant dut.fifo.wr_en : std_logic>>
       << constant dut.fifo.wr_en : std_logic     >>

    **Fix**

    .. code-block:: vhdl

       << constant dut.fifo.wr_en : std_logic >>
       << constant dut.fifo.wr_en : std_logic >>
    """

    def __init__(self):
        Rule.__init__(self, [token.double_greater_than])
