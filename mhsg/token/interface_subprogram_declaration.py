# -*- coding: utf-8 -*-

from mhsg import parser


class is_keyword(parser.keyword):
    """
    unique_id = interface_subprogram_declaration : is_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)
