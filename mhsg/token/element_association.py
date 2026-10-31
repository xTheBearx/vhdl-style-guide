# -*- coding: utf-8 -*-

from mhsg import parser


class assignment(parser.assignment):
    """
    unique_id = element_association : assignment
    """

    def __init__(self, sString):
        super().__init__(sString)
