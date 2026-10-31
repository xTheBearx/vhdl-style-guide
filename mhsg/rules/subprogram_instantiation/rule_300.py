# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_indent

lTokens = []
lTokens.append(token.subprogram_kind.procedure_keyword)
lTokens.append(token.subprogram_kind.function_keyword)


class rule_300(token_indent):
    """
    This rule checks the indent of the subprogram instantiation.

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
