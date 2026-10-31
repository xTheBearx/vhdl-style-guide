# -*- coding: utf-8 -*-

from mhsg.vhdlFile.classify import interface_list


def classify(iToken, lObjects):
    """
    port_list ::=
        *port*_interface_list
    """

    return interface_list.classify(iToken, lObjects)
