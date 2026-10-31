# -*- coding: utf-8 -*-
"""
Renames a declaration and every reference to it in the region it is declared in.

Only local declarations are renamed: those in an architecture, process, block, generate, subprogram body or package body.
Declarations other files can see, in entities, package declarations, ports and generics, are never renamed.
"""

from mhsg import parser, token
from mhsg.rules import consistent_case_utils as cc_utils

lLocalScopes = ["architecture", "process", "subprogram", "block", "package_body", "generate"]

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


def rename(oFile, iDeclaration, sNewName):
    """
    Renames the declaration at index iDeclaration and its references to sNewName.
    Returns False, and changes nothing, if the declaration is not local or the new name is already used in the file.
    """
    lAllTokens = oFile.lAllObjects
    oDeclarations = oFile.get_declarations()
    lDeclarations = [oDeclaration for oDeclaration in oDeclarations.declarations if oDeclaration.index == iDeclaration]
    if len(lDeclarations) == 0 or lDeclarations[0].scope.kind not in lLocalScopes:
        return False
    oDeclaration = lDeclarations[0]
    sNewLower = sNewName.lower()
    if len(oDeclarations.find_all(sNewName)) > 0 or any(not isinstance(oToken, lNotNames) and get_prefix(oToken) == sNewLower for oToken in lAllTokens):
        return False

    oScope = oDeclaration.scope
    lRecordElementNames = cc_utils.get_record_element_names(oFile)
    lOtherDeclarations = {oOther.index for oOther in oDeclarations.declarations if oOther is not oDeclaration}
    for iToken in range(oScope.start, oScope.end + 1):
        oToken = lAllTokens[iToken]
        if isinstance(oToken, lNotNames) or isinstance(oToken, token.association_element.formal_part):
            continue
        if get_prefix(oToken) != oDeclaration.lower_name or iToken in lOtherDeclarations:
            continue
        # The name must refer to this declaration, not to one with the same name in a nested scope or to a record element
        if iToken != iDeclaration:
            lFound = oDeclarations.find(oToken.get_value().split(".")[0], iToken)
            if len(lFound) == 0 or lFound[0] is not oDeclaration:
                continue
        if "." not in oToken.get_value() and cc_utils.is_record_element_choice(oToken.get_value(), iToken, lAllTokens, lRecordElementNames):
            continue
        lSegments = oToken.get_value().split(".")
        lSegments[0] = sNewName
        oToken.set_value(".".join(lSegments))
    oFile.clear_declarations()
    return True


def get_prefix(oToken):
    sValue = oToken.get_value()
    if sValue is None:
        return None
    return sValue.split(".")[0].lower()
