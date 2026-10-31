# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case

lTokens = []
lTokens.append(token.package_declaration.end_package_keyword)


class rule_018(token_case):
    """
    This rule checks the **package** keyword in the **end package** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       end PACKAGE fifo_pkg;

    **Fix**

    .. code-block:: vhdl

       end package fifo_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
