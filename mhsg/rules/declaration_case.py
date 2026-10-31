# -*- coding: utf-8 -*-
"""
Finds names spelled with a different case than the declaration they refer to, using the declaration list.
"""

from mhsg import parser, token
from mhsg.rules import consistent_case_utils as cc_utils

# Tokens whose value is not a name
lNotNames = (
    parser.comment,
    parser.whitespace,
    parser.carriage_return,
    parser.blank_line,
    parser.character_literal,
    parser.string_literal,
    parser.keyword,
)


def find_inconsistent_names(oFile, fDeclaration, fName=None):
    """
    Returns (index, token, declared name) for each simple name which refers to a declaration accepted by fDeclaration
    but is spelled with a different case. fName can limit the names checked, given the token index and the declaration list.
    """
    lReturn = []
    lAllTokens = oFile.lAllObjects
    oDeclarations = oFile.get_declarations()
    lRecordElementNames = cc_utils.get_record_element_names(oFile)
    for iToken, oToken in enumerate(lAllTokens):
        if isinstance(oToken, lNotNames) or isinstance(oToken, token.association_element.formal_part):
            continue
        sName = oToken.get_value()
        if sName is None or len(sName) == 0 or not (sName[0].isalpha()) or "." in sName:
            continue
        if cc_utils.is_record_element_choice(sName, iToken, lAllTokens, lRecordElementNames):
            continue
        if fName is not None and not fName(iToken, oDeclarations):
            continue
        lFound = oDeclarations.find(sName, iToken)
        if len(lFound) == 0 or lFound[0].index == iToken or not fDeclaration(lFound[0]):
            continue
        sDeclared = lAllTokens[lFound[0].index].get_value()
        if sDeclared != sName:
            lReturn.append((iToken, oToken, sDeclared))
    return lReturn
