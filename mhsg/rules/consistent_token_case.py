# -*- coding: utf-8 -*-

from mhsg import violation
from mhsg.rule_group import case
from mhsg.rules import consistent_case_utils as cc_utils
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.extract import tokens


class consistent_token_case(case.Rule):
    """
    Checks the case for words.

    Parameters
    ----------

    name : string
       The group the rule belongs to.

    identifier : string
       unique identifier.  Usually in the form of 00N.

    lTokens: list of token type objects
       token type to apply the case check against
    """

    def __init__(self, lTokens, lNames, lIgnore=None):
        super().__init__()
        self.subphase = 2
        self.lTokens = lTokens
        self.lNames = lNames
        # Only check names inside the scope the declaration is in, for example generics used in their entity
        self.bNamesInDeclaringScopeOnly = False
        # Only check names of declarations of these kinds, for example generic, see vhdlFile/declarations.py
        self.lDeclarationKinds = None
        # Only check names of declarations in scopes of these kinds, for example entity
        self.lDeclarationScopes = None
        if lIgnore is None:
            self.lIgnoreTokens = []
        else:
            self.lIgnoreTokens = lIgnore
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        return get_names_with_inconsistent_case(
            oFile,
            self.lNames,
            self.lTokens,
            self.bNamesInDeclaringScopeOnly,
            self.lDeclarationKinds,
            self.lDeclarationScopes,
        )

    def _analyze(self, lToi):
        for oToi in lToi:
            iLine, lTokens = utils.get_toi_parameters(oToi)
            sExpected = oToi.get_meta_data("expected")
            sActual = lTokens[0].get_value()
            sSolution = f"Change {sActual} to {sExpected}"
            oViolation = violation.New(iLine, oToi, sSolution)
            dAction = {}
            dAction["expected"] = sExpected
            oViolation.set_action(dAction)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        dActions = oViolation.get_action()
        lTokens[0].set_value(dActions["expected"])
        oViolation.set_tokens(lTokens)


def get_names_with_inconsistent_case(oFile, lNames, lDeclarationTokens, bNamesInDeclaringScopeOnly=False, lDeclarationKinds=None, lDeclarationScopes=None):
    """
    Returns the names which refer to a declaration of one of the declaration token types, but are spelled with a different case.
    The declaration list decides what each name refers to, so a declaration in an inner scope hides one in an outer scope.
    """
    lReturn = []
    lAllTokens = oFile.lAllObjects
    oTokenMap = oFile.get_token_map()
    oDeclarations = oFile.get_declarations()
    lRecordElementNames = cc_utils.get_record_element_names(oFile)
    tDeclarationTokens = tuple(lDeclarationTokens)
    lIndexes = sorted({iIndex for oName in lNames for iIndex in oTokenMap.get_token_indexes(oName)})
    for iName in lIndexes:
        oName = lAllTokens[iName]
        sName = oName.get_value()
        if cc_utils.is_record_element_choice(sName, iName, lAllTokens, lRecordElementNames):
            continue
        lFound = oDeclarations.find(sName, iName)
        if len(lFound) == 0:
            continue
        oDeclaration = lFound[0]
        if oDeclaration.index == iName or not isinstance(lAllTokens[oDeclaration.index], tDeclarationTokens):
            continue
        if lDeclarationKinds is not None and oDeclaration.kind not in lDeclarationKinds:
            continue
        if lDeclarationScopes is not None and oDeclaration.scope.kind not in lDeclarationScopes:
            continue
        if bNamesInDeclaringScopeOnly and not oDeclaration.scope.contains(iName):
            continue
        sDeclared = lAllTokens[oDeclaration.index].get_value()
        if sDeclared != sName:
            oToi = tokens.New(iName, oTokenMap.get_line_number_of_index(iName), [oName])
            oToi.set_meta_data("expected", sDeclared)
            lReturn.append(oToi)
    return lReturn
