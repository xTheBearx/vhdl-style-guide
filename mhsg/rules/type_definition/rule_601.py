# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.incomplete_type_declaration.identifier)
lTokens.append(token.full_type_declaration.identifier)


class rule_601(token_prefix):
    """
    This rule checks for valid prefixes on type identifiers declared in packages and package bodies.
    Types declared inside subprograms are not checked by this rule.
    The default prefix is *t_*.

    When this rule is enabled, rule type_015 no longer checks types declared in packages, so packages and other code can use different prefixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         type state is (idle, run);

       end package my_pkg;

    **Fix**

    With :code:`prefixes = ['pt_']`:

    .. code-block:: vhdl

       package my_pkg is

         type pt_state is (idle, run);

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.prefixes = ["t_"]
        self.solution = "Type identifiers"
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "type_015"
