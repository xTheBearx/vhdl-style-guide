# -*- coding: utf-8 -*-

from mhsg import parser


class to(parser.keyword):
    """
    unique_id = direction : to
    """

    def __init__(self, sString):
        super().__init__(sString)


class downto(parser.keyword):
    """
    unique_id = direction : downto
    """

    def __init__(self, sString):
        super().__init__(sString)
