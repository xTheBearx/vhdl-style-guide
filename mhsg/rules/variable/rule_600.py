# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.variable_declaration.identifier)


class rule_600(token_suffix):
    """
    This rule checks for valid suffix on variable identifiers.
    The default variable suffix is *_v*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames variables declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the suffixes is added. Names starting with one of :code:`remove_suffixes` lose it first (for example width_const becomes width_c).
       Variables which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       variable my_var : natural;

    **Fix**

    .. code-block:: vhdl

       variable my_var_v : natural;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_suffixes")
        self.suffixes = ["_v"]
        self.solution = "Variable identifiers"
