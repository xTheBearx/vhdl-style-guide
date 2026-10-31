# -*- coding: utf-8 -*-

from mhsg import parser


class colon(parser.colon):
    """
    unique_id = component_specification : colon
    """

    def __init__(self, sString):
        super().__init__(sString)


class component_name(parser.name):
    """
    unique_id = component_specification : component_name
    """

    def __init__(self, sString):
        super().__init__(sString)
