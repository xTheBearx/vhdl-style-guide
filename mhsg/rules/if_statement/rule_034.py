# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.if_statement.end_if_keyword)


class rule_034(token_case):
    """
    This rule checks the **if** keyword in the **end if** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       end If;

       end IF;

    **Fix**

    .. code-block:: vhdl

       end if;

       end if;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
