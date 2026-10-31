# -*- coding: utf-8 -*-

from mhsg import parser


class identifier(parser.identifier):
    """
    unique_id = interface_unknown_declaration : identifier
    """

    def __init__(self, sString):
        super().__init__(sString)


class colon(parser.colon):
    """
    unique_id = interface_unknown_declaration : colon
    """

    def __init__(self, sString=":"):
        super().__init__()
