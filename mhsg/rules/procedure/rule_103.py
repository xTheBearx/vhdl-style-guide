# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.procedure_specification.designator, token.procedure_specification.open_parenthesis])


class rule_103(Rule):
    """
    This rule checks for a single space between the procedure designator and the open parenthesis.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       procedure average_samples    (

    **Fix**

    .. code-block:: vhdl

       procedure average_samples (
    """

    def __init__(self):
        super().__init__(lTokens)
