# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent

lTokens = []
lTokens.append(token.loop_statement.loop_keyword)


class rule_300(token_indent):
    """
    This rule checks the indentation of the **loop** keyword.

    **Violation**

    .. code-block:: vhdl

       fifo_proc : process () is
       begin

           loop

         end loop;

       end process;

    **Fix**

    .. code-block:: vhdl

       fifo_proc : process () is
       begin

         loop

         end loop;

       end process;
    """

    def __init__(self):
        super().__init__(lTokens)
