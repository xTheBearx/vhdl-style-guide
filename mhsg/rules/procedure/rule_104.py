# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([token.procedure_specification.designator, token.subprogram_body.is_keyword])
lTokens.append([token.procedure_specification.close_parenthesis, token.subprogram_body.is_keyword])


class rule_104(Rule):
    """
    This rule checks for a single space before the **is** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       )    is

    **Fix**

    .. code-block:: vhdl

       ) is
    """

    def __init__(self):
        super().__init__(lTokens)
