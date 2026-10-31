# -*- coding: utf-8 -*-

from mhsg.vhdlFile.classify import primary_unit, secondary_unit


def detect(iToken, lObjects):
    """
    library_unit ::=
        primary_unit
      | secondary_unit
    """

    iCurrent = primary_unit.detect(iToken, lObjects)
    if iCurrent != iToken:
        return iCurrent

    iCurrent = secondary_unit.detect(iToken, lObjects)
    if iCurrent != iToken:
        return iCurrent

    return iToken
