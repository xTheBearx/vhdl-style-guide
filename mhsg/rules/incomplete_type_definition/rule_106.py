# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.incomplete_type_definition.array_keyword)


class rule_106(Rule):
    """
    This rule checks for whitespace after the **array** keyword.
    The default of no whitespace matches unbounded_array_definition_100.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is array (type is range <>) of type is private;
       type t_data is array     (type is range <>) of type is private;

    **Fix**

    .. code-block:: vhdl

       type t_data is array(type is range <>) of type is private;
       type t_data is array(type is range <>) of type is private;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.number_of_spaces = 0
