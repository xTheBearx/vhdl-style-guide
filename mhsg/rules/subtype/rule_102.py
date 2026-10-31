# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.subtype_declaration.is_keyword)


class rule_102(Rule):
    """
    This rule checks for a single space after the **is** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       subtype counter is     unsigned(4 downto 0);

    **Fix**

    .. code-block:: vhdl

       subtype counter is unsigned(4 downto 0);
    """

    def __init__(self):
        super().__init__(lTokens)
