# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_suffix import token_suffix

lTokens = []
lTokens.append(token.signal_declaration.identifier)


class rule_600(token_suffix):
    """
    This rule checks for valid suffixes on signal identifiers.
    Default signal suffix is *_s*.

    .. NOTE:: With :code:`fixable` set to :code:`true`, the fix renames signals declared in an architecture, process, block, subprogram body or package body, and every reference to them in the same region.
       The first of the suffixes is added. Names starting with one of :code:`remove_suffixes` lose it first (for example width_const becomes width_c).
       Signals which other files can see, in entities and package declarations, are never renamed.

    |configuring_prefix_and_suffix_rules_link|

    **Violation**

    .. code-block:: vhdl

       signal wr_en : std_logic;
       signal rd_en : std_logic;

    **Fix**

    .. code-block:: vhdl

       signal wr_en_s : std_logic;
       signal rd_en_s : std_logic;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.bRenameLocalDeclarations = True
        self.configuration.append("remove_suffixes")
        self.suffixes = ["_s"]
        self.solution = "Signal identifiers"
