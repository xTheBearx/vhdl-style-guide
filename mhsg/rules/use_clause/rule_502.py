# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case as Rule

lTokens = []
lTokens.append(token.use_clause.item_name)


class rule_502(Rule):
    """
    This rule checks the item name called out in the selected name has proper case.

    .. NOTE:: The item is usually declared in a package in another file, so this rule cannot know what kind of item it is or how it is spelled where it is declared.
       If items are imported whose declarations follow a different case, for example constants in upper case, either:

       * set :code:`case` to :code:`upper_or_lower` to accept items in all upper case or all lower case, or
       * list patterns matching those items in :code:`regex_exceptions`, for example :code:`'c_'` for constants named with a :code:`c_` prefix.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       use my_lib.Increment;

    **Fix**

    .. code-block:: vhdl

       use my_lib.increment;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::name")
        self.configuration.append("case_exceptions")
        self.configuration.append("regex_exceptions")
