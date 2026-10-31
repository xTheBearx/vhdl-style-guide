# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.split_line_at_token import split_line_at_token

lTokens = []
lTokens.append(token.if_statement.end_keyword)


class rule_020(split_line_at_token):
    """
    This rule checks the **end if** keyword is on its own line.

    **Violation**

    .. code-block:: vhdl

       if (a = '1') then c <= '1'; else c <= '0'; end if;

    **Fix**

    .. code-block:: vhdl

       if (a = '1') then c <= '1'; else c <= '0';
       end if;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.solution = "Move *end if* keywords to their own line."
