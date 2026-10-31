# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.function_specification.function_keyword, token.function_specification.designator])


class rule_103(Rule):
    """
    This rule checks for a single space after the **function** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       function    func_1 (

    **Fix**

    .. code-block:: vhdl

       function func_1 (
    """

    def __init__(self):
        super().__init__(lTokens)
