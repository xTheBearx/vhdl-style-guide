# -*- coding: utf-8 -*-

from mhsg import parser, token
from mhsg.vhdlFile.extract import utils
from mhsg.vhdlFile.extract.get_line_preceding_line import get_line_preceding_line


def get_blank_lines_above_line_starting_with_use_clause(lTokens, lAllTokens, oTokenMap):
    lIndexes = get_list_of_indexes(lTokens, oTokenMap)
    lToi = utils.get_all_blank_lines_above_indexes(lIndexes, lAllTokens, oTokenMap)
    lToi = filter_design_unit(lToi, oTokenMap)
    for oToi in lToi:
        previous_library = get_previous_library(oToi, lAllTokens, oTokenMap)
        current_library = get_current_library(oToi, lAllTokens, oTokenMap)
        previous_library_is_different = (previous_library == current_library) or (previous_library is None)
        oToi.set_meta_data("previous_library_is_different", previous_library_is_different)

    return lToi


def get_lines_above_use_clause_from_different_library(lTokens, lAllTokens, oTokenMap):
    """
    Returns the line directly above each use clause when that line names a different library.
    """
    lReturn = []
    for iIndex in get_list_of_indexes(lTokens, oTokenMap):
        iLine = oTokenMap.get_line_number_of_index(iIndex)
        if iLine == 1:
            continue
        sCurrentLibrary = get_library_on_line(iLine, lAllTokens, oTokenMap)
        sPreviousLibrary = get_library_on_line(iLine - 1, lAllTokens, oTokenMap)
        if sCurrentLibrary is None or sPreviousLibrary is None:
            continue
        if sCurrentLibrary != sPreviousLibrary:
            lReturn.append(get_line_preceding_line(iLine, lAllTokens, 1, oTokenMap))
    return lReturn


def get_library_on_line(iLine, lAllTokens, oTokenMap):
    iStartIndex = oTokenMap.get_index_of_line(iLine)
    iEndIndex = oTokenMap.get_index_of_line(iLine + 1)
    for oLibraryNameToken in [token.use_clause.library_name, token.logical_name_list.logical_name]:
        lTokenIndex = oTokenMap.get_token_indexes_between_indexes(oLibraryNameToken, iStartIndex, iEndIndex)
        if len(lTokenIndex) > 0:
            return lAllTokens[lTokenIndex[0]].get_lower_value()
    return None


def get_previous_library(oToi, lAllTokens, oTokenMap):
    iEndIndex = oToi.get_start_index()
    iLineNumber = oTokenMap.get_line_number_of_index(iEndIndex)
    iStartIndex = oTokenMap.get_index_of_line(iLineNumber)

    # Check for both possible clauses that could contain a library name: use clause and library clause (which includes
    # the library name in logical_name_list).
    for oLibraryNameToken in [token.use_clause.library_name, token.logical_name_list.logical_name]:
        lTokenIndex = oTokenMap.get_token_indexes_between_indexes(oLibraryNameToken, iStartIndex, iEndIndex)
        if len(lTokenIndex) > 0:
            oToken = lAllTokens[lTokenIndex[0]]
            return oToken.get_lower_value()
    # If no library name was found, return None.
    return None


def get_current_library(oToi, lAllTokens, oTokenMap):
    iLineNumber = oToi.get_line_number()
    iStartIndex = oTokenMap.get_index_of_line(iLineNumber)
    iLineNumber += 1
    iEndIndex = oTokenMap.get_index_of_line(iLineNumber)
    lTokenIndex = oTokenMap.get_token_indexes_between_indexes(token.use_clause.library_name, iStartIndex, iEndIndex)
    oToken = lAllTokens[lTokenIndex[0]]
    return oToken.get_lower_value()


def get_list_of_indexes(lTokens, oTokenMap):
    lIndexes = utils.get_indexes_of_token_list(lTokens, oTokenMap)
    lIndexes = utils.filter_indexes_which_start_a_line(lIndexes, oTokenMap)
    return lIndexes


def filter_design_unit(lToi, oTokenMap):
    lReturn = filter_context_clause(lToi, oTokenMap)
    lReturn = filter_library_unit(lReturn, oTokenMap)
    return lReturn


def filter_context_clause(lToi, oTokenMap):
    return filter_context_reference(lToi, oTokenMap)


def filter_library_unit(lToi, oTokenMap):
    lReturn = filter_primary_unit(lToi, oTokenMap)
    lReturn = filter_secondary_unit(lReturn, oTokenMap)
    return lReturn


def filter_primary_unit(lToi, oTokenMap):
    lReturn = filter_entity_declaration(lToi, oTokenMap)
    lReturn = filter_configuration_declaration(lReturn, oTokenMap)
    lReturn = filter_package_declaration(lReturn, oTokenMap)
    lReturn = filter_package_instantiation_declaration(lReturn, oTokenMap)
    lReturn = filter_context_declaration(lReturn, oTokenMap)
    return lReturn


def filter_secondary_unit(lToi, oTokenMap):
    lReturn = filter_architecture_body(lToi, oTokenMap)
    lReturn = filter_package_body(lReturn, oTokenMap)
    return lReturn


def filter_architecture_body(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.architecture_body.semicolon)


def filter_package_body(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.package_body.semicolon)


def filter_entity_declaration(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.entity_declaration.semicolon)


def filter_configuration_declaration(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.configuration_declaration.semicolon)


def filter_package_declaration(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.package_declaration.semicolon)


def filter_package_instantiation_declaration(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.package_instantiation_declaration.semicolon)


def filter_context_declaration(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.context_declaration.semicolon)


def filter_context_reference(lToi, oTokenMap):
    return filter_based_on_token(lToi, oTokenMap, token.context_reference.semicolon)


def filter_based_on_token(lToi, oTokenMap, oToken):
    lReturn = []
    for oToi in lToi:
        iIndex = oToi.iStartIndex
        if not oTokenMap.is_previous_non_whitespace_token(iIndex, oToken):
            lReturn.append(oToi)
    return lReturn
