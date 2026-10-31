# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import blank_line_below_line_ending_with_token

lTokens = []
lTokens.append(token.if_statement.then_keyword)

lOverrides = []
lOverrides.append(token.case_statement.case_label)
lOverrides.append(token.case_statement.case_keyword)
lOverrides.append(token.loop_statement.loop_label)
lOverrides.append(token.loop_statement.loop_keyword)
lOverrides.append(token.iteration_scheme.while_keyword)
lOverrides.append(token.iteration_scheme.for_keyword)


class rule_200(blank_line_below_line_ending_with_token):
    """
    This rule checks for blank lines below the **then** keyword.

    |configuring_blank_lines_link|

    The default style is :code:`no_blank_line`.
    With this style, one blank line is allowed if the next line starts a **case** or **loop** statement.

    **Violation**

    .. code-block:: vhdl

       if (a = '1') then


         b <= '0';

    **Fix**

    .. code-block:: vhdl

       if (a = '1') then
         b <= '0';
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
        self.lOverrides = lOverrides
