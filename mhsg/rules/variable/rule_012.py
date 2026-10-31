# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.variable_declaration.identifier)


class rule_012(token_prefix):
    """
    This rule checks for valid prefixes on variable identifiers.
    The default variable prefix is *v_*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames variables declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the prefixes is added. Names starting with one of :code:`remove_prefixes` lose it first (for example const_width becomes c_width).
       Variables which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       variable my_var : natural;

    **Fix**

    .. code-block:: vhdl

       variable v_my_var : natural;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_prefixes")
        self.prefixes = ["v_"]
        self.solution = "Variable identifiers"
