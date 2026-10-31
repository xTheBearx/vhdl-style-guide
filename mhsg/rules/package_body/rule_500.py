# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.package_body.package_keyword)


class rule_500(token_case):
    """
    This rule checks the **package** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       PACKAGE body FIFO_PKG is

    **Fix**

    .. code-block:: vhdl

       package body FIFO_PKG is
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
