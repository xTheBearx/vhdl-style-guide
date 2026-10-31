# -*- coding: utf-8 -*-

from mhsg import parser, token
from mhsg.rules.whitespace_between_token_pairs import Rule

lTokens = []
lTokens.append([parser.type, token.subprogram_body.is_keyword])
lTokens.append([token.type_mark.name, token.subprogram_body.is_keyword])


class rule_107(Rule):
    """
    This rule checks for a single space before the **is** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       ) return integer    is

    **Fix**

    .. code-block:: vhdl

       ) return integer is
    """

    def __init__(self):
        super().__init__(lTokens)
