# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.function_specification.designator, token.function_specification.return_keyword])
lTokens.append([token.function_specification.close_parenthesis, token.function_specification.return_keyword])


class rule_105(Rule):
    """
    This rule checks for a single space before the **return** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       )    return integer is

    **Fix**

    .. code-block:: vhdl

       ) return integer is
    """

    def __init__(self):
        super().__init__(lTokens)
