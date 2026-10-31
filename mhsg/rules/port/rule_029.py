# -*- coding: utf-8 -*-

from mhsg.rules import ordered_list_utils
from mhsg.rules.section_comment import Rule


class rule_029(Rule):
    """
    This rule checks each group of ports has a section comment above it.

    .. NOTE:: This rule is disabled by default.

    A group of ports is separated from the next group by a blank line or a comment line.
    At least one of the comment lines directly above the first port of each group must match the :code:`section_pattern` option, a regular expression.
    The default pattern accepts any comment.
    For example, :code:`'^-- [A-Z]'` requires a comment starting with a capital letter.

    This rule only reports groups without a section comment, because it cannot know their names.
    port_028 sorts the ports within each section.

    **Violation**

    .. code-block:: vhdl

       port (
         clk : in  std_logic;
         rst : in  std_logic;

         data_o : out std_logic
       );

    **Fix**

    .. code-block:: vhdl

       port (
         -- Clocks and resets
         clk : in  std_logic;
         rst : in  std_logic;

         -- Data
         data_o : out std_logic
       );
    """

    def __init__(self):
        super().__init__(ordered_list_utils.get_port_clauses, "ports")
