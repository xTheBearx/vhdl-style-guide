# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import structure
from mhsg.rules import ordered_list_utils


class rule_029(structure.Rule):
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
        super().__init__()
        self.solution = "Add a section comment above this group of ports"
        self.phase = 1
        self.disable = True
        self.fixable = False
        self.section_pattern = "^--"
        self.configuration.append("section_pattern")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        for oToi in ordered_list_utils.get_port_clauses(oFile):
            for lSection in ordered_list_utils.get_sections(ordered_list_utils.get_elements(oToi)):
                dFirst = lSection[0]
                oSection = oToi.extract_tokens(dFirst["start"], dFirst["start"])
                # extract_tokens shares the meta data of oToi, and each section needs its own
                oSection.dMetaData = {}
                oSection.set_meta_data("line", dFirst["line"])
                oSection.set_meta_data("header", dFirst["header"])
                lReturn.append(oSection)
        return lReturn

    def _analyze(self, lToi):
        oPattern = re.compile(self.section_pattern)
        for oToi in lToi:
            if any(oPattern.search(sComment) for sComment in oToi.get_meta_data("header")):
                continue
            self.add_violation(violation.New(oToi.get_meta_data("line"), oToi, self.solution))
