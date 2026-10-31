# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.procedure_specification.procedure_keyword, token.procedure_specification.designator])


class rule_102(Rule):
    """
    This rule checks for a single space after the **procedure** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       procedure    average_samples (

    **Fix**

    .. code-block:: vhdl

       procedure average_samples (
    """

    def __init__(self):
        super().__init__(lTokens)
