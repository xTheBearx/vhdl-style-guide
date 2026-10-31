# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent

lTokens = []
lTokens.append(token.package_body.end_keyword)


class rule_301(token_indent):
    """
    This rule checks the indent of the end package declaration.

    **Violation**

    .. code-block:: vhdl

       package body FIFO_PKG is

          end package body fifo_pkg;

    **Fix**

    .. code-block:: vhdl

       package body fifo_pkg is

       end package body fifo_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
