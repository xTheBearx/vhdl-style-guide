# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import concurrent_statement


def detect(iToken, lObjects):
    """
    block_statement_part ::=
        { concurrent_statement }
    """

    return utils.detect_submodule(iToken, lObjects, concurrent_statement)
