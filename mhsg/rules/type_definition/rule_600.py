# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.incomplete_type_declaration.identifier)
lTokens.append(token.full_type_declaration.identifier)


class rule_600(token_suffix):
    """
    This rule checks for valid suffixes in user defined type identifiers.
    The default new type suffix is *_t*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames types declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the suffixes is added. Names starting with one of :code:`remove_suffixes` lose it first (for example width_const becomes width_c).
       Types which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       type my_type is range -5 to 5 ;

    **Fix**

    .. code-block:: vhdl

       type my_type_t is range -5 to 5 ;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_suffixes")
        self.suffixes = ["_t"]
        self.solution = "Type identifiers"
