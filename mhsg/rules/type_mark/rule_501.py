# -*- coding: utf-8 -*-

from mhsg import parser, project_index, token
from mhsg.rules import utils
from mhsg.rules.token_case_with_prefix_suffix import token_case_with_prefix_suffix
from mhsg.vhdlFile.extract import tokens

# Tokens which can name the type in a type conversion, such as todo.name in x <= unsigned(y)
lNameTokens = (token.todo.name, token.association_element.actual_part, parser.todo)


class rule_501(token_case_with_prefix_suffix):
    """
    This rule checks the type mark in a type conversion has proper case.

    A name followed by parentheses is a type conversion if it names a standard or IEEE type, such as **std_logic_vector** or **unsigned**,
    or a type or subtype declared in one of the files checked in the same run.
    Other names followed by parentheses are function calls or indexes and are not checked.
    Type conversions to types declared in the same file are checked by :ref:`type_014` instead, which keeps them consistent with the declaration.

    .. NOTE:: This rule is disabled by default.
       Configure it with the same case as :ref:`type_mark_500` to treat type conversions like other type marks.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       data <= STD_LOGIC_VECTOR(count);

    **Fix**

    .. code-block:: vhdl

       data <= std_logic_vector(count);
    """

    def __init__(self):
        super().__init__([])
        self.disable = True
        self.groups.append("case::name")

    def _get_tokens_of_interest(self, oFile):
        self.case_exceptions_lower = utils.lowercase_list(self.case_exceptions)
        lAllTokens = oFile.lAllObjects
        oDeclarations = oFile.get_declarations()
        lProjectTypeNames = getattr(oFile.configuration, "project_type_names", set())
        oTokenMap = oFile.get_token_map()
        lReturn = []
        for iToken, oToken in enumerate(lAllTokens):
            if type(oToken) not in lNameTokens or not is_followed_by_open_parenthesis(iToken, lAllTokens):
                continue
            sName = oToken.get_value().split(".")[-1]
            if len(oDeclarations.find(sName, iToken)) > 0:
                # Declared in this file: type_014 checks types, and other names are not types
                continue
            if sName.lower() in project_index.STANDARD_TYPE_NAMES or sName.lower() in lProjectTypeNames:
                lReturn.append(tokens.New(iToken, oTokenMap.get_line_number_of_index(iToken), [oToken]))
        return lReturn


def is_followed_by_open_parenthesis(iToken, lAllTokens):
    for oToken in lAllTokens[iToken + 1 :]:
        if isinstance(oToken, parser.whitespace):
            continue
        return isinstance(oToken, parser.open_parenthesis)
    return False
