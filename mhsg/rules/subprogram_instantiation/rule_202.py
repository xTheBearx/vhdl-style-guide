# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import blank_line_below_line_ending_with_token

lTokens = []
lTokens.append(token.subprogram_instantiation_declaration.semicolon)


class rule_202(blank_line_below_line_ending_with_token):
    """
    This rule checks for a blank line below the end of the subprogram instantiation.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       function my_func is new my_generic_func
         generic map (
           test => 2
         );
       constant c_width : integer := 8;

    **Fix**

    .. code-block:: vhdl

       function my_func is new my_generic_func
         generic map (
           test => 2
         );

       constant c_width : integer := 8;
    """

    def __init__(self):
        super().__init__(lTokens)
