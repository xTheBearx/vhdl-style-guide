# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.case_statement.end_case_keyword)


class rule_018(token_case):
    """
    This rule checks the **case** keyword has proper case in the **end case**.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

          end CASE;
          end CAse;
          end case;

    **Fix**

    .. code-block:: vhdl

          end case;
          end case;
          end case;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
