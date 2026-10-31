# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import package_scope
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.subtype_declaration.identifier)


class rule_602(token_suffix):
    """
    This rule checks for valid suffixes on subtype identifiers declared in packages and package bodies.
    Subtypes declared inside subprograms are not checked by this rule.
    The default suffix is *_st*.

    When this rule is enabled, rule subtype_600 no longer checks subtypes declared in packages, so packages and other code can use different suffixes.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       package my_pkg is

         subtype byte is std_logic_vector(7 downto 0);

       end package my_pkg;

    **Fix**

    With :code:`suffixes = ['_pst']`:

    .. code-block:: vhdl

       package my_pkg is

         subtype byte_pst is std_logic_vector(7 downto 0);

       end package my_pkg;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.suffixes = ["_st"]
        self.package_scope = package_scope.ONLY_PACKAGES
        self.general_rule = "subtype_600"
