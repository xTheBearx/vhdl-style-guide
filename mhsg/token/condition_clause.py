# -*- coding: utf-8 -*-

from mhsg import parser


class until_keyword(parser.keyword):
    """
    unique_id = condition_clause : until_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
