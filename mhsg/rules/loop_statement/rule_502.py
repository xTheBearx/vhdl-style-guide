# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case as Rule

lTokens = []
lTokens.append(token.loop_statement.end_loop_keyword)


class rule_502(Rule):
    """
    This rule checks the **loop** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       while (condition) loop

       end LOOP;

    **Fix**

    .. code-block:: vhdl

       while (condition) loop

       end loop;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
