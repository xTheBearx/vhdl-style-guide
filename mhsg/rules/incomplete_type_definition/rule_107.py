# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_before_token import Rule

lTokens = []
lTokens.append(token.incomplete_type_definition.dot)


class rule_107(Rule):
    """
    This rule checks for whitespace before the **.** of a floating incomplete type definition.
    The default of a single space matches the form :code:`range <> . <>` used in the LRM.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is range <>. <>;
       type t_data is range <>    . <>;

    **Fix**

    .. code-block:: vhdl

       type t_data is range <> . <>;
       type t_data is range <> . <>;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.number_of_spaces = 1
