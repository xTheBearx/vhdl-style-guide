# -*- coding: utf-8 -*-

from mhsg import token

# Values of the package_scope attribute of the prefix and suffix rules
ALL = None
ONLY_PACKAGES = "only"
EXCLUDE_PACKAGES = "exclude"


def filter_tokens_of_interest(lToi, oFile, sPackageScope):
    """
    Keeps the tokens of interest matching the package scope.
    A token is in a package if it is declared in a package or package body, but not inside a subprogram body.
    """
    if sPackageScope is ALL:
        return lToi
    lRegions = get_package_regions(oFile)
    lReturn = []
    for oToi in lToi:
        bInPackage = is_index_in_regions(oToi.get_start_index(), lRegions)
        if bInPackage == (sPackageScope == ONLY_PACKAGES):
            lReturn.append(oToi)
    return lReturn


def get_package_regions(oFile):
    oTokenMap = oFile.get_token_map()
    lPackages = _get_regions(oTokenMap, token.package_declaration.package_keyword, token.package_declaration.end_keyword)
    lPackages.extend(_get_regions(oTokenMap, token.package_body.package_keyword, token.package_body.end_keyword))
    lSubprograms = _get_regions(oTokenMap, token.subprogram_body.is_keyword, token.subprogram_body.end_keyword)
    return [(tPackage, [tSubprogram for tSubprogram in lSubprograms if tPackage[0] < tSubprogram[0] < tPackage[1]]) for tPackage in lPackages]


def is_index_in_regions(iIndex, lRegions):
    for tPackage, lSubprograms in lRegions:
        if tPackage[0] < iIndex < tPackage[1]:
            for tSubprogram in lSubprograms:
                if tSubprogram[0] < iIndex < tSubprogram[1]:
                    return False
            return True
    return False


def _get_regions(oTokenMap, oStart, oEnd):
    """
    Pairs each start token with the end token closing it, allowing for nesting.
    """
    lEvents = [(iIndex, 1) for iIndex in oTokenMap.get_token_indexes(oStart)]
    lEvents.extend([(iIndex, -1) for iIndex in oTokenMap.get_token_indexes(oEnd)])
    lEvents.sort()
    lReturn = []
    lStack = []
    for iIndex, iType in lEvents:
        if iType == 1:
            lStack.append(iIndex)
        elif len(lStack) > 0:
            lReturn.append((lStack.pop(), iIndex))
    return lReturn
