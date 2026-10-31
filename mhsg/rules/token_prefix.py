# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import naming
from mhsg.rules import package_scope, rename_local_declaration


class token_prefix(naming.Rule):
    """
    Checks the prefix for words.

    Parameters
    ----------

    name : string
       The group the rule belongs to.

    identifier : string
       unique identifier.  Usually in the form of 00N.

    lTokens : list of parser object types
       object types to check the prefix

    lPrefixes : string list
       acceptable prefixes
    """

    def __init__(self, lTokens):
        super().__init__()
        self.lTokens = lTokens
        self.prefixes = []
        self.configuration.append("prefixes")
        # Rules for local declarations can rename them when fixable is enabled
        self.bRenameLocalDeclarations = False
        self.remove_prefixes = []
        # Set by the rule list when a companion rule checks names in packages, see package_scope.py
        self.package_scope = package_scope.ALL
        self.fixable = False
        self.disable = True
        self.exceptions = []
        self.configuration.append("exceptions")
        self.regexp_exceptions = []

    def _get_tokens_of_interest(self, oFile):
        return package_scope.filter_tokens_of_interest(oFile.get_tokens_matching(self.lTokens), oFile, self.package_scope)

    def _analyze(self, lToi):
        self.generate_regexp_exceptions()

        lPrefixLower = []
        for sPrefix in self.prefixes:
            lPrefixLower.append(sPrefix.lower())

        for oToi in lToi:
            lTokens = oToi.get_tokens()
            sToken = lTokens[0].get_lower_value()

            if self.exception_found(sToken):
                continue

            bValid = False
            for sPrefix in lPrefixLower:
                if sToken.startswith(sPrefix.lower()):
                    bValid = True
            if not bValid:
                sSolution = "Prefix " + lTokens[0].get_value() + " with one of the following: " + ", ".join(self.prefixes)
                oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
                self.add_violation(oViolation)

    def fix(self, oFile, dFixOnly=None):
        """
        Renames local declarations which violate the rule, and every reference to them.
        Only rules which set bRenameLocalDeclarations support this, and only when fixable is enabled.
        """
        if not self.fixable or not self.bRenameLocalDeclarations or len(self.prefixes) == 0:
            return
        self.analyze(oFile)
        self._filter_out_fix_only_violations(dFixOnly)
        for oViolation in self.violations:
            iIndex = oViolation.oTokens.get_start_index()
            oToken = oFile.lAllObjects[iIndex]
            if rename_local_declaration.rename(oFile, iIndex, self._new_name(oToken)):
                self.had_violations = True
        self.clear_violations()

    def _new_name(self, oToken):
        sName = oToken.get_value()
        for sRemove in self.remove_prefixes:
            if sName.lower().startswith(sRemove.lower()):
                sName = sName[len(sRemove) :]
                break
        return self.prefixes[0] + sName

    def generate_regexp_exceptions(self):
        self.regexp_exceptions = []
        for exception in self.exceptions:
            regexp = re.compile(exception, re.IGNORECASE)
            self.regexp_exceptions.append(regexp)

    def exception_found(self, sToken):
        for regexp in self.regexp_exceptions:
            if regexp.match(sToken) is not None:
                return True
        return False
