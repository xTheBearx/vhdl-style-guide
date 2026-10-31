# -*- coding: utf-8 -*-

from mhsg import parser


class range_keyword(parser.keyword):
    """
    unique_id = range_constraint : range_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
