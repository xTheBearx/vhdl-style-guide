# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent

lTokens = []
lTokens.append(token.case_statement.case_label)


class rule_300(token_indent):
    """
    This rule checks the indentation of the label.

    **Violation**

    .. code-block:: vhdl

       case_label : case data is

      end case;

    **Fix**

    .. code-block:: vhdl

      case_label : case data is

      end case;
    """

    def __init__(self):
        super().__init__(lTokens)
