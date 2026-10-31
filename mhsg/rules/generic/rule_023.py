# -*- coding: utf-8 -*-

from mhsg.rules import ordered_list_utils
from mhsg.rules.section_comment import Rule


class rule_023(Rule):
    """
    This rule checks each group of generics has a section comment above it.

    .. NOTE:: This rule is disabled by default.

    A group of generics is separated from the next group by a blank line or a comment line.
    At least one of the comment lines directly above the first generic of each group must match the :code:`section_pattern` option, a regular expression.
    The default pattern accepts any comment.
    For example, :code:`'^-- [A-Z]'` requires a comment starting with a capital letter.

    This rule only reports groups without a section comment, because it cannot know their names.
    generic_022 checks the order of the generics within each section.

    **Violation**

    .. code-block:: vhdl

       generic (
         G_ADDR_WIDTH : integer := 8;
         G_DATA_WIDTH : integer := 32;

         G_DEBUG : boolean := false
       );

    **Fix**

    .. code-block:: vhdl

       generic (
         -- Bus widths
         G_ADDR_WIDTH : integer := 8;
         G_DATA_WIDTH : integer := 32;

         -- Simulation
         G_DEBUG : boolean := false
       );
    """

    def __init__(self):
        super().__init__(ordered_list_utils.get_generic_clauses, "generics")
