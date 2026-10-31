# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.extract import tokens


def get_lines_with_length_that_exceed_column(iColumn, lAllTokens, oTokenMap):
    iLine = 1
    lReturn = []
    lTemp = []
    iStart = None
    bFirstTokenInLine = False
    for iToken, oToken in enumerate(lAllTokens):
        if isinstance(oToken, parser.carriage_return):
            if utils.does_length_of_tokens_exceed(lTemp, iColumn):
                lReturn.append(tokens.New(iStart, iLine, lTemp))
            iLine += 1
            lTemp = []
            bFirstTokenInLine = True
            continue

        lTemp.append(oToken)

        if bFirstTokenInLine:
            iStart = iToken

    return lReturn
