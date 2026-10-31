# -*- coding: utf-8 -*-

from mhsg.token import process_statement as token
from mhsg.vhdlFile.extract.get_tokens_bounded_by import get_tokens_bounded_by

oStart = token.process_keyword
oEnd = token.begin_keyword


def extract(lAllTokens, oTokenMap):
    return get_tokens_bounded_by(oStart, oEnd, lAllTokens, oTokenMap)
