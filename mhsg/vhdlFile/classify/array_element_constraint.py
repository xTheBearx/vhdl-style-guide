# -*- coding: utf-8 -*-

from mhsg.vhdlFile.classify import element_constraint


def detect(iToken, lObjects):
    """
    array_element_constraint ::= element_constraint
    """
    return element_constraint.detect(iToken, lObjects)
