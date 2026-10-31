# -*- coding: utf-8 -*-

from mhsg import parser


class identifier(parser.identifier):
    """
    unique_id = identifier : identifier
    """

    def __init__(self, sString):
        super().__init__(sString)
