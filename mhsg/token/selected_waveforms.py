# -*- coding: utf-8 -*-

from mhsg import parser


class when_keyword(parser.keyword):
    """
    unique_id = selected_waveforms : when_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class comma(parser.comma):
    """
    unique_id = selected_waveforms : comma
    """

    def __init__(self, sString=","):
        super().__init__(sString)
