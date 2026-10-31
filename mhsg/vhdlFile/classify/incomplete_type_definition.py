# -*- coding: utf-8 -*-

from mhsg.token import (
    incomplete_type_definition as token,
    index_subtype_definition as index_token,
)
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import (
    discrete_range,
    index_constraint,
    subtype_indication,
    type_mark,
    unspecified_type_indication,
)


def classify(iToken, lObjects):
    """
    incomplete_type_definition ::=
        private_incomplete_type_definition
      | scalar_incomplete_type_definition
      | discrete_incomplete_type_definition
      | integer_incomplete_type_definition
      | physical_incomplete_type_definition
      | floating_incomplete_type_definition
      | array_incomplete_type_definition
      | access_incomplete_type_definition
      | file_incomplete_type_definition

    private_incomplete_type_definition ::= private
    scalar_incomplete_type_definition ::= <>
    discrete_incomplete_type_definition ::= ( <> )
    integer_incomplete_type_definition ::= range <>
    physical_incomplete_type_definition ::= units <>
    floating_incomplete_type_definition ::= range <> . <>
    array_incomplete_type_definition ::=
        array ( array_index_incomplete_type_list ) of element_incomplete_subtype_indication
    access_incomplete_type_definition ::= access access_incomplete_subtype_indication
    file_incomplete_type_definition ::= file of file_incomplete_type_mark
    """
    if utils.is_next_token("private", iToken, lObjects):
        return utils.assign_next_token_required("private", token.private_keyword, iToken, lObjects)

    if utils.is_next_token("<>", iToken, lObjects):
        return utils.assign_next_token_required("<>", token.undefined_range, iToken, lObjects)

    if utils.is_next_token("(", iToken, lObjects):
        iCurrent = utils.assign_next_token_required("(", token.open_parenthesis, iToken, lObjects)
        iCurrent = utils.assign_next_token_required("<>", token.undefined_range, iCurrent, lObjects)
        return utils.assign_next_token_required(")", token.close_parenthesis, iCurrent, lObjects)

    if utils.is_next_token("range", iToken, lObjects):
        iCurrent = utils.assign_next_token_required("range", token.range_keyword, iToken, lObjects)
        iCurrent = utils.assign_next_token_required("<>", token.undefined_range, iCurrent, lObjects)
        if utils.is_next_token(".", iCurrent, lObjects):
            iCurrent = utils.assign_next_token_required(".", token.dot, iCurrent, lObjects)
            iCurrent = utils.assign_next_token_required("<>", token.undefined_range, iCurrent, lObjects)
        return iCurrent

    if utils.is_next_token("units", iToken, lObjects):
        iCurrent = utils.assign_next_token_required("units", token.units_keyword, iToken, lObjects)
        return utils.assign_next_token_required("<>", token.undefined_range, iCurrent, lObjects)

    if utils.is_next_token("array", iToken, lObjects):
        return classify_array(iToken, lObjects)

    if utils.is_next_token("access", iToken, lObjects):
        iCurrent = utils.assign_next_token_required("access", token.access_keyword, iToken, lObjects)
        return classify_incomplete_subtype_indication(iCurrent, lObjects)

    if utils.is_next_token("file", iToken, lObjects):
        iCurrent = utils.assign_next_token_required("file", token.file_keyword, iToken, lObjects)
        iCurrent = utils.assign_next_token_required("of", token.of_keyword, iCurrent, lObjects)
        if unspecified_type_indication.detect(iCurrent, lObjects):
            return unspecified_type_indication.classify(iCurrent, lObjects)
        return type_mark.classify(iCurrent, lObjects)

    # Not a valid incomplete type definition.  Report the error at the next token.
    return utils.assign_next_token_required("private", token.private_keyword, iToken, lObjects)


def classify_array(iToken, lObjects):
    """
    array_index_incomplete_type_list ::=
        array_index_incomplete_type { , array_index_incomplete_type }

    array_index_incomplete_type ::=
        index_subtype_definition
      | index_constraint
      | unspecified_type_indication
    """
    iCurrent = utils.assign_next_token_required("array", token.array_keyword, iToken, lObjects)
    iCurrent = utils.assign_next_token_required("(", token.open_parenthesis, iCurrent, lObjects)
    while True:
        iCurrent = classify_array_index_incomplete_type(iCurrent, lObjects)
        if not utils.is_next_token(",", iCurrent, lObjects):
            break
        iCurrent = utils.assign_next_token_required(",", token.comma, iCurrent, lObjects)
    iCurrent = utils.assign_next_token_required(")", token.close_parenthesis, iCurrent, lObjects)
    iCurrent = utils.assign_next_token_required("of", token.of_keyword, iCurrent, lObjects)
    return classify_incomplete_subtype_indication(iCurrent, lObjects)


def classify_array_index_incomplete_type(iToken, lObjects):
    if unspecified_type_indication.detect(iToken, lObjects):
        return unspecified_type_indication.classify(iToken, lObjects)
    if index_constraint.detect(iToken, lObjects):
        return index_constraint.classify(iToken, lObjects)
    if is_index_subtype_definition(iToken, lObjects):
        iCurrent = type_mark.classify(iToken, lObjects)
        iCurrent = utils.assign_next_token_required("range", index_token.range_keyword, iCurrent, lObjects)
        return utils.assign_next_token_required("<>", index_token.undefined_range, iCurrent, lObjects)
    # A discrete range, such as "natural range 0 to 7"
    return discrete_range.classify_until([","], iToken, lObjects)


def is_index_subtype_definition(iToken, lObjects):
    """Returns True if the next tokens are: type_mark range <>"""
    return utils.are_next_consecutive_tokens([None, "range", "<>"], iToken, lObjects)


def classify_incomplete_subtype_indication(iToken, lObjects):
    """
    element_incomplete_subtype_indication ::=
        subtype_indication
      | unspecified_type_indication
    """
    if unspecified_type_indication.detect(iToken, lObjects):
        return unspecified_type_indication.classify(iToken, lObjects)
    return subtype_indication.classify(iToken, lObjects)
