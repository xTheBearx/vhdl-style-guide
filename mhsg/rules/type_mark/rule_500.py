# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import utils
from mhsg.rules.token_case_with_prefix_suffix import token_case_with_prefix_suffix
from mhsg.vhdlFile.extract import tokens

lTokens = []
lTokens.append(token.type_mark.name)

lDeclarationTokens = []
lDeclarationTokens.append(token.incomplete_type_declaration.identifier)
lDeclarationTokens.append(token.full_type_declaration.identifier)
lDeclarationTokens.append(token.subtype_declaration.identifier)


class rule_500(token_case_with_prefix_suffix):
    """
    This rule checks that the type marks without declarations in the current file have proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

      signal my_sig : MY_TYPE_MARK;

    **Fix**

    .. code-block:: vhdl

      signal my_sig : my_type_mark;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::name")

    def _get_tokens_of_interest(self, oFile):
        """
        Returns the type marks which do not refer to a type or subtype declared in the file.
        Type marks of types declared in the file are checked by type_014 and subtype_002, which follow the declaration.
        """
        self.case_exceptions_lower = utils.lowercase_list(self.case_exceptions)
        lAllTokens = oFile.lAllObjects
        oDeclarations = oFile.get_declarations()
        oTokenMap = oFile.get_token_map()
        lReturn = []
        for iName in oTokenMap.get_token_indexes(token.type_mark.name):
            oName = lAllTokens[iName]
            lFound = oDeclarations.find(oName.get_value(), iName)
            if len(lFound) > 0 and isinstance(lAllTokens[lFound[0].index], tuple(lDeclarationTokens)):
                continue
            lReturn.append(tokens.New(iName, oTokenMap.get_line_number_of_index(iName), [oName]))
        return lReturn
