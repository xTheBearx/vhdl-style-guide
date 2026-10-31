# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.case_generate_statement.case_keyword)


class rule_100(Rule):
    """
    This rule checks for a single space after the **case** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       case    data generate


    **Fix**

    .. code-block:: vhdl

       case data generate
    """

    def __init__(self):
        Rule.__init__(self, lTokens)
