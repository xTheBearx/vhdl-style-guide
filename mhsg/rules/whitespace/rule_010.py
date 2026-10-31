# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.n_spaces_before_and_after_tokens import n_spaces_before_and_after_tokens

lTokens = []
lTokens.append(token.adding_operator.concat)


class rule_010(n_spaces_before_and_after_tokens):
    """
    This rule checks for spaces before and after the concatenate (&) operator.

    **Violation**

    .. code-block:: vhdl

       a <= b&c;

    **Fix**

    .. code-block:: vhdl

       a <= b & c;
    """

    def __init__(self):
        super().__init__(1, lTokens)
        self.solution = "Ensure a single space before and after concat operator."
        self.configuration_documentation_link = None
