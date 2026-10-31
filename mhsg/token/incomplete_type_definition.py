# -*- coding: utf-8 -*-

from mhsg import parser


class private_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : private_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class range_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : range_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class units_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : units_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class array_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : array_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class of_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : of_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class access_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : access_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class file_keyword(parser.keyword):
    """
    unique_id = incomplete_type_definition : file_keyword
    """

    def __init__(self, sString):
        super().__init__(sString)


class undefined_range(parser.undefined_range):
    """
    unique_id = incomplete_type_definition : undefined_range
    """

    def __init__(self, sString="<>"):
        super().__init__()


class open_parenthesis(parser.open_parenthesis):
    """
    unique_id = incomplete_type_definition : open_parenthesis
    """

    def __init__(self, sString="("):
        super().__init__()


class close_parenthesis(parser.close_parenthesis):
    """
    unique_id = incomplete_type_definition : close_parenthesis
    """

    def __init__(self, sString=")"):
        super().__init__()


class comma(parser.comma):
    """
    unique_id = incomplete_type_definition : comma
    """

    def __init__(self, sString=","):
        super().__init__()


class dot(parser.dot):
    """
    unique_id = incomplete_type_definition : dot
    """

    def __init__(self, sString="."):
        super().__init__()
