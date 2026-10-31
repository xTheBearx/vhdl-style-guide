# -*- coding: utf-8 -*-

from mhsg import parser, token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.function_specification.return_keyword, token.type_mark.name])
lTokens.append([token.function_specification.return_keyword, parser.type])


class rule_106(Rule):
    """
    This rule checks for a single space after the **return** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       ) return    integer is

    **Fix**

    .. code-block:: vhdl

       ) return integer is
    """

    def __init__(self):
        super().__init__(lTokens)
