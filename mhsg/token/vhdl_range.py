# -*- coding: utf-8 -*-

from mhsg import parser


class vhdl_range(parser.item):
    """
    unique_id = vhdl_range : vhdl_range
    """

    def __init__(self, sString):
        super().__init__(sString)
