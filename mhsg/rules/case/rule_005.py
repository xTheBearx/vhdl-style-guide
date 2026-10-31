# -*- coding: utf-8 -*-

from mhsg.rules.whitespace_before_token import Rule
from mhsg.token import case_statement_alternative as token


class rule_005(Rule):
    """
    This rule checks for a single space before the **=>** operator.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

      case data is

        when 3   =>

    **Fix**

    .. code-block:: vhdl

      case data is

        when 3 =>
    """

    def __init__(self):
        super().__init__([token.assignment])
