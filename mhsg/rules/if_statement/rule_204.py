# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.previous_line import previous_line

lTokens = []
lTokens.append(token.if_statement.end_keyword)

lOverrides = []
lOverrides.append(token.case_statement.semicolon)
lOverrides.append(token.loop_statement.semicolon)


class rule_204(previous_line):
    """
    This rule checks for blank lines or comments above the **end if** keywords.

    |configuring_previous_line_rules_link|

    The default style is :code:`no_blank_line`.
    With this style, one blank line is allowed if the previous line ends a **case** or **loop** statement.

    **Violation**

    .. code-block:: vhdl

         e <= '0';


       end if;

    **Fix**

    .. code-block:: vhdl

         e <= '0';
       end if;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
        self.lOverrides = lOverrides
