# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.subtype_declaration.identifier)


class rule_004(token_prefix):
    """
    This rule checks for valid prefixes in subtype identifiers.
    The default new subtype prefix is *st_*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames subtypes declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the prefixes is added. Names starting with one of :code:`remove_prefixes` lose it first (for example const_width becomes c_width).
       Subtypes which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       subtype my_subtype is range 0 to 9;

    **Fix**

    .. code-block:: vhdl

       subtype st_my_subtype is range 0 to 9;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_prefixes")
        self.prefixes = ["st_"]
