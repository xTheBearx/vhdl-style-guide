# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.function_specification.pure_keyword, token.function_specification.function_keyword])
lTokens.append([token.function_specification.impure_keyword, token.function_specification.function_keyword])


class rule_102(Rule):
    """
    This rule checks for a single space between the **pure** or **impure** keyword and the **function** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       impure    function func_1 (

    **Fix**

    .. code-block:: vhdl

       impure function func_1 (
    """

    def __init__(self):
        super().__init__(lTokens)
