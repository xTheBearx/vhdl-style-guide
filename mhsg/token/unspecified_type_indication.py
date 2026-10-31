# -*- coding: utf-8 -*-

from mhsg import parser


class type_keyword(parser.keyword):
    """
    unique_id = unspecified_type_indication : type_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class is_keyword(parser.keyword):
    """
    unique_id = unspecified_type_indication : is_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
