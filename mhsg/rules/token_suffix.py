# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import naming
from mhsg.rules import package_scope, rename_local_declaration


class token_suffix(naming.Rule):
    """
    Checks the suffix of a token.

    Parameters
    ----------

    name : string
       The group the rule belongs to.

    identifier : string
       unique identifier.  Usually in the form of 00N.

    lTokens : list of parser object types
       object types to check the prefix

    lSuffixes: string list
       acceptable suffixes
    """

    def __init__(self, lTokens):
        super().__init__()
        self.lTokens = lTokens
        self.suffixes = []
        self.configuration.append("suffixes")
        # Rules for local declarations can rename them when fixable is enabled
        self.bRenameLocalDeclarations = False
        self.remove_suffixes = []
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

        lSuffixLower = []
        for sSuffix in self.suffixes:
            lSuffixLower.append(sSuffix.lower())

        for oToi in lToi:
            lTokens = oToi.get_tokens()
            sToken = lTokens[0].get_lower_value()

            if self.exception_found(sToken):
                continue

            bValid = False
            for sSuffix in lSuffixLower:
                if sToken.endswith(sSuffix):
                    bValid = True
            if not bValid:
                sSolution = "Suffix " + lTokens[0].get_value() + " with one of the following: " + ", ".join(self.suffixes)
                oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
                self.add_violation(oViolation)

    def fix(self, oFile, dFixOnly=None):
        """
        Renames local declarations which violate the rule, and every reference to them.
        Only rules which set bRenameLocalDeclarations support this, and only when fixable is enabled.
        """
        if not self.fixable or not self.bRenameLocalDeclarations or len(self.suffixes) == 0:
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
        for sRemove in self.remove_suffixes:
            if sName.lower().endswith(sRemove.lower()):
                sName = sName[: len(sName) - len(sRemove)]
                break
        return sName + self.suffixes[0]

    def generate_regexp_exceptions(self):
        for exception in self.exceptions:
            regexp = re.compile(exception, re.IGNORECASE)
            self.regexp_exceptions.append(regexp)

    def exception_found(self, sToken):
        for regexp in self.regexp_exceptions:
            if regexp.match(sToken) is not None:
                return True
        return False
