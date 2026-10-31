# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case as Rule

lTokens = []
lTokens.append(token.case_generate_alternative.when_keyword)


class rule_500(Rule):
    """
    This rule checks the **when** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       WHEN choices =>

    **Fix**

    .. code-block:: vhdl

       when choices =>
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
