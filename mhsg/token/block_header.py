# -*- coding: utf-8 -*-

from mhsg import parser


class semicolon(parser.semicolon):
    """
    unique_id = block_header : semicolon
    """

    def __init__(self, sString=";"):
        super().__init__()
