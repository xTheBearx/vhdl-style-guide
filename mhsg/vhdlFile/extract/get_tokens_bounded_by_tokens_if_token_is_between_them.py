# -*- coding: utf-8 -*-

from mhsg.vhdlFile.extract import tokens


def get_tokens_bounded_by_tokens_if_token_is_between_them(oStart, oEnd, oToken, lAllObjects, oTokenMap):
    """
    Returns the tokens from each start token to its matching end token, if
    oToken is between them.  An oToken that belongs to a nested pair, such as
    a record type declared inside a protected type body, does not count for
    the enclosing pair.  Each pair is returned at most once.
    """
    lReturn = []

    lStart, lEnd = oTokenMap.get_token_pair_indexes(oStart, oEnd)
    lPairs = list(zip(lStart, lEnd))

    lIndexes = oTokenMap.get_token_indexes(oToken)

    for iStart, iEnd in lPairs:
        for iIndex in lIndexes:
            if not iStart < iIndex < iEnd:
                continue
            if is_inside_nested_pair(iIndex, iStart, iEnd, lPairs):
                continue
            lTemp = lAllObjects[iStart : iEnd + 1]
            iStartLine = oTokenMap.get_line_number_of_index(iStart)
            oToi = tokens.New(iStart, iStartLine, lTemp)
            oToi.set_token_value(iIndex - iStart)
            lReturn.append(oToi)
            break

    return lReturn


def is_inside_nested_pair(iIndex, iStart, iEnd, lPairs):
    for iNestedStart, iNestedEnd in lPairs:
        if iStart < iNestedStart < iIndex < iNestedEnd < iEnd:
            return True
    return False
