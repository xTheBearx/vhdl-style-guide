# -*- coding: utf-8 -*-

from mhsg.token import unspecified_type_indication as token
from mhsg.vhdlFile import utils


def detect(iToken, lObjects):
    """
    unspecified_type_indication ::=
        type is incomplete_type_definition
    """
    return utils.are_next_consecutive_tokens(["type", "is"], iToken, lObjects)


def classify(iToken, lObjects):
    # Imported here because incomplete_type_definition imports this module
    from mhsg.vhdlFile.classify import (
        incomplete_type_definition,  # pylint: disable=import-outside-toplevel
    )

    iCurrent = utils.assign_next_token_required("type", token.type_keyword, iToken, lObjects)
    iCurrent = utils.assign_next_token_required("is", token.is_keyword, iCurrent, lObjects)
    return incomplete_type_definition.classify(iCurrent, lObjects)
