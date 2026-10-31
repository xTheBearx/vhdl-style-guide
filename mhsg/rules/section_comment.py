# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import structure
from mhsg.rules import ordered_list_utils


class Rule(structure.Rule):
    """
    Checks each group of declarations in a list, separated by blank lines or
    comment lines, has a comment matching section_pattern directly above it.

    fGetLists(oFile) returns the tokens of each list, from its open to its close parenthesis.
    """

    def __init__(self, fGetLists, sNoun):
        super().__init__()
        self.fGetLists = fGetLists
        self.solution = "Add a section comment above this group of " + sNoun
        self.phase = 1
        self.disable = True
        self.fixable = False
        self.section_pattern = "^--"
        self.configuration.append("section_pattern")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        for oToi in self.fGetLists(oFile):
            for lSection in ordered_list_utils.get_sections(ordered_list_utils.get_interface_elements(oToi)):
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
