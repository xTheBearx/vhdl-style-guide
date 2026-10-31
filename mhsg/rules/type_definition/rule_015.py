# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.incomplete_type_declaration.identifier)
lTokens.append(token.full_type_declaration.identifier)


class rule_015(token_prefix):
    """
    This rule checks for valid prefixes in user defined type identifiers.
    The default new type prefix is *t_*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames types declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the prefixes is added. Names starting with one of :code:`remove_prefixes` lose it first (for example const_width becomes c_width).
       Types which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       type my_type is range -5 to 5 ;

    **Fix**

    .. code-block:: vhdl

       type t_my_type is range -5 to 5 ;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_prefixes")
        self.prefixes = ["t_"]
        self.solution = "Type identifiers"
