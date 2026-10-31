# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_prefix import token_prefix

lTokens = []
lTokens.append(token.signal_declaration.identifier)


class rule_008(token_prefix):
    """
    This rule checks for valid prefixes on signal identifiers.
    Default signal prefix is *s_*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames signals declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the prefixes is added. Names starting with one of :code:`remove_prefixes` lose it first (for example const_width becomes c_width).
       Signals which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       signal wr_en : std_logic;
       signal rd_en : std_logic;

    **Fix**

    .. code-block:: vhdl

       signal s_wr_en : std_logic;
       signal s_rd_en : std_logic;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_prefixes")
        self.prefixes = ["s_"]
        self.solution = "Signal identifiers"
