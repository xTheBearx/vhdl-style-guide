# -*- coding: utf-8 -*-

from mhsg import parser


class for_keyword(parser.keyword):
    """
    unique_id = timeout_clause : for_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
