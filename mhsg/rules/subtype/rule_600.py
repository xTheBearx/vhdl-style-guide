# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.subtype_declaration.identifier)


class rule_600(token_suffix):
    """
    This rule checks for valid suffixes in subtype identifiers.
    The default new subtype suffix is *_st*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames subtypes declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the suffixes is added. Names starting with one of :code:`remove_suffixes` lose it first (for example width_const becomes width_c).
       Subtypes which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       subtype my_subtype is range 0 to 9;

    **Fix**

    .. code-block:: vhdl

       subtype my_subtype_st is range 0 to 9;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_suffixes")
        self.suffixes = ["_st"]
