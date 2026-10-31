# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import blank_line_below_line_ending_with_token

lTokens = []
lTokens.append(token.subprogram_instantiation_declaration.uninstantiated_subprogram_name)


class rule_201(blank_line_below_line_ending_with_token):
    """
    This rule checks for blank lines below the subprogram instantiation.

    |configuring_blank_lines_link|

    The default style is :code:`no_blank_line`.

    **Violation**

    .. code-block:: vhdl

       function my_func is new my_generic_func

         generic map (

    **Fix**

    .. code-block:: vhdl

       function my_func is new my_generic_func
         generic map (
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
