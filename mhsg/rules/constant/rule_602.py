# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.constant_declaration.identifier)


class rule_602(token_suffix):
    """
    This rule checks for valid suffixes on constant identifiers declared in packages and package bodies.
    Constants declared inside subprograms are not checked by this rule.
    The default suffix is *_c*.

    When this rule is enabled, rule constant_600 no longer checks constants declared in packages, so packages and other code can use different suffixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         constant width : integer := 8;

       end package my_pkg;

    **Fix**

    With :code:`suffixes = ['_pc']`:

    .. code-block:: vhdl

       package my_pkg is

         constant width_pc : integer := 8;

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.suffixes = ["_c"]
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "constant_600"
