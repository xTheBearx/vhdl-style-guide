# -*- coding: utf-8 -*-
"""
Renames a declaration and every reference to it in the region it is declared in.

Only local declarations are renamed: those in an architecture, process, block, subprogram body or package body.
Declarations other files can see, in entities, package declarations, ports and generics, are never renamed.
"""

from mhsg import parser, token
from mhsg.rules import consistent_case_utils as cc_utils

lLocalScopes = ["architecture_body", "process", "subprogram_body", "block_statement", "package_body"]

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


def get_scopes(oFile):
    lReturn = []
    lReturn.extend(cc_utils.get_architecture_indexes(oFile))
    lReturn.extend(cc_utils.get_process_indexes(oFile))
    lReturn.extend(cc_utils.get_subprogram_body_indexes(oFile))
    lReturn.extend(cc_utils.get_block_indexes(oFile))
    lReturn.extend(cc_utils.get_package_body_indexes(oFile))
    lReturn.extend(cc_utils.get_package_declaration_indexes(oFile))
    lReturn.extend(cc_utils.get_entity_declaration_indexes(oFile))
    lReturn.extend(cc_utils.get_component_declaration_indexes(oFile))
    return lReturn


def get_innermost_scope(iIndex, lScopes):
    lContaining = [dScope for dScope in lScopes if dScope["keyword"] < iIndex < dScope["end"]]
    if len(lContaining) == 0:
        return None
    return min(lContaining, key=lambda dScope: dScope["end"] - dScope["keyword"])


def rename(oFile, iDeclaration, sNewName, lScopes):
    """
    Renames the declaration at index iDeclaration and its references to sNewName.
    Returns False, and changes nothing, if the declaration is not local or the new name is already used in the file.
    """
    lAllTokens = oFile.lAllObjects
    dScope = get_innermost_scope(iDeclaration, lScopes)
    if dScope is None or dScope["type"] not in lLocalScopes:
        return False
    sOldLower = lAllTokens[iDeclaration].get_value().lower()
    sNewLower = sNewName.lower()
    if any(not isinstance(oToken, lNotNames) and sNewLower in name_segments(oToken) for oToken in lAllTokens):
        return False

    lRecordElementNames = cc_utils.get_record_element_names(oFile)
    lRecordElements = get_record_element_declaration_indexes(lAllTokens)
    lHidden = get_hidden_ranges(iDeclaration, sOldLower, dScope, lAllTokens, lScopes)
    for iToken in range(dScope["keyword"], dScope["end"] + 1):
        if any(iStart < iToken < iEnd for iStart, iEnd in lHidden) or iToken in lRecordElements:
            continue
        oToken = lAllTokens[iToken]
        if isinstance(oToken, lNotNames) or isinstance(oToken, token.association_element.formal_part):
            continue
        sValue = oToken.get_value()
        if sValue is None:
            continue
        lSegments = sValue.split(".")
        if lSegments[0].lower() != sOldLower:
            continue
        if len(lSegments) == 1 and sOldLower in lRecordElementNames and cc_utils.is_record_element_choice(sValue, iToken, lAllTokens, lRecordElementNames):
            continue
        lSegments[0] = sNewName
        oToken.set_value(".".join(lSegments))
    return True


def name_segments(oToken):
    sValue = oToken.get_value()
    if sValue is None:
        return []
    return [sSegment.lower() for sSegment in sValue.split(".")[:1]]


def get_hidden_ranges(iDeclaration, sOldLower, dScope, lAllTokens, lScopes):
    """
    Returns the regions nested in the scope which declare their own object with the same name.
    """
    lReturn = []
    for iToken in range(dScope["keyword"], dScope["end"] + 1):
        if iToken == iDeclaration:
            continue
        oToken = lAllTokens[iToken]
        if isinstance(oToken, parser.identifier) and oToken.get_value().lower() == sOldLower:
            dInner = get_innermost_scope(iToken, lScopes)
            if dInner is not None and dInner is not dScope:
                lReturn.append((dInner["keyword"], dInner["end"]))
    return lReturn


def get_record_element_declaration_indexes(lAllTokens):
    lReturn = set()
    bInRecord = False
    for iToken, oToken in enumerate(lAllTokens):
        if isinstance(oToken, token.record_type_definition.record_keyword):
            bInRecord = True
        elif isinstance(oToken, token.record_type_definition.end_keyword):
            bInRecord = False
        elif bInRecord and isinstance(oToken, token.identifier_list.identifier):
            lReturn.add(iToken)
    return lReturn
