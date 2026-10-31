# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope, token_prefix

lTokens = []
lTokens.append(token.subtype_declaration.identifier)


class rule_601(token_prefix):
    """
    This rule checks for valid prefixes on subtype identifiers declared in packages and package bodies.
    Subtypes declared inside subprograms are not checked by this rule.
    The default prefix is *st_*.

    When this rule is enabled, rule subtype_004 no longer checks subtypes declared in packages, so packages and other code can use different prefixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         subtype byte is std_logic_vector(7 downto 0);

       end package my_pkg;

    **Fix**

    With :code:`prefixes = ['pst_']`:

    .. code-block:: vhdl

       package my_pkg is

         subtype pst_byte is std_logic_vector(7 downto 0);

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.prefixes = ["st_"]
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "subtype_004"
