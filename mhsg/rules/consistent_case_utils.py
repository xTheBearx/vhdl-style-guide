# -*- coding: utf-8 -*-
"""
Helpers shared by the rules which check names against their declarations.
"""

from mhsg import parser, token


def get_record_element_names(oFile):
    lReturn = []
    bInRecord = False
    for oToken in oFile.lAllObjects:
        if isinstance(oToken, token.record_type_definition.record_keyword):
            bInRecord = True
        elif isinstance(oToken, token.record_type_definition.end_keyword):
            bInRecord = False
        elif bInRecord and isinstance(oToken, token.identifier_list.identifier):
            lReturn.append(oToken.get_value().lower())
    return lReturn


def is_record_element_choice(sToken, iToken, lTokens, lRecordElementNames):
    """
    Returns True if the token is the choice of a named association, as in `NAME => value`, and names a record element.
    """
    if lRecordElementNames is None or sToken.lower() not in lRecordElementNames:
        return False
    for oToken in lTokens[iToken + 1 :]:
        if isinstance(oToken, parser.whitespace):
            continue
        return isinstance(oToken, token.element_association.assignment)
    return False
