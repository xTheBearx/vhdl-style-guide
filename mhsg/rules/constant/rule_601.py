# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.constant_declaration.identifier)


class rule_601(token_prefix):
    """
    This rule checks for valid prefixes on constant identifiers declared in packages and package bodies.
    Constants declared inside subprograms are not checked by this rule.
    The default prefix is *c_*.

    When this rule is enabled, rule constant_015 no longer checks constants declared in packages, so packages and other code can use different prefixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         constant width : integer := 8;

       end package my_pkg;

    **Fix**

    With :code:`prefixes = ['pc_']`:

    .. code-block:: vhdl

       package my_pkg is

         constant pc_width : integer := 8;

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.prefixes = ["c_"]
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "constant_015"
