# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import design_unit


def tokenize(lObjects):
    """
    design_file ::=
        design_unit { design_unit }
    """
    iCurrent = 0
    while iCurrent < len(lObjects):
        iReturn = design_unit.detect(iCurrent, lObjects)
        if iReturn == iCurrent:
            iCurrent += 1
        else:
            iCurrent = iReturn
