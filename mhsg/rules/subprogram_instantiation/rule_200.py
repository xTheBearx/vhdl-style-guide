# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import previous_line

lTokens = []
lTokens.append(token.subprogram_kind.procedure_keyword)
lTokens.append(token.subprogram_kind.function_keyword)


class rule_200(previous_line):
    """
    This rule checks for blank lines or comments above the **procedure** or **function** keyword of a subprogram instantiation.

    |configuring_previous_line_rules_link|

    The default style is :code:`no_code`.

    **Violation**

    .. code-block:: vhdl

       constant c_width : integer := 8;
       function my_func is new my_generic_func

    **Fix**

    .. code-block:: vhdl

       constant c_width : integer := 8;

       function my_func is new my_generic_func
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_code"
