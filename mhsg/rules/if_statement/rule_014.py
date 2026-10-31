# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_indent

lTokens = []
lTokens.append(token.if_statement.end_keyword)


class rule_014(token_indent):
    """
    This rule checks the indent of the **end if** keyword.

    **Violation**

    .. code-block:: vhdl

      if (a = '1') then
        b <= '0'
      elsif (c = '1') then
        d <= '1';
      else
        e <= '0';
        end if;

    **Fix**

    .. code-block:: vhdl

      if (a = '1') then
        b <= '0'
      elsif (c = '1') then
        d <= '1';
      else
        e <= '0';
      end if;
    """

    def __init__(self):
        super().__init__(lTokens)
