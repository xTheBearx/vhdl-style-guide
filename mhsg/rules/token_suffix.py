# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import naming
from mhsg.rules import package_scope


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
        self.suffixes = None
        self.configuration.append("suffixes")
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

    def generate_regexp_exceptions(self):
        for exception in self.exceptions:
            regexp = re.compile(exception, re.IGNORECASE)
            self.regexp_exceptions.append(regexp)

    def exception_found(self, sToken):
        for regexp in self.regexp_exceptions:
            if regexp.match(sToken) is not None:
                return True
        return False
