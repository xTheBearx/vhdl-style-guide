# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.incomplete_type_declaration.identifier)
lTokens.append(token.full_type_declaration.identifier)


class rule_602(token_suffix):
    """
    This rule checks for valid suffixes on type identifiers declared in packages and package bodies.
    Types declared inside subprograms are not checked by this rule.
    The default suffix is *_t*.

    When this rule is enabled, rule type_600 no longer checks types declared in packages, so packages and other code can use different suffixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         type state is (idle, run);

       end package my_pkg;

    **Fix**

    With :code:`suffixes = ['_pt']`:

    .. code-block:: vhdl

       package my_pkg is

         type state_pt is (idle, run);

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.suffixes = ["_t"]
        self.solution = "Type identifiers"
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "type_600"
