# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.token import direction
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import (
    external_constant_name,
    external_signal_name,
    external_variable_name,
)


def detect(iToken, lObjects):
    """
    external_name ::=
        external_constant_name
      | external_signal_name
      | external_variable_name
    """

    iReturn = external_constant_name.detect(iToken, lObjects)
    if iReturn != iToken:
        return iReturn

    iReturn = external_signal_name.detect(iToken, lObjects)
    if iReturn != iToken:
        return iReturn

    iReturn = external_variable_name.detect(iToken, lObjects)
    if iReturn != iToken:
        return iReturn

    return iToken
