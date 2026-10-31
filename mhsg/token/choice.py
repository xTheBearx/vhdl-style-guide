# -*- coding: utf-8 -*-

from mhsg import parser


class others_keyword(parser.keyword):
    """
    unique_id = choice : others_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
