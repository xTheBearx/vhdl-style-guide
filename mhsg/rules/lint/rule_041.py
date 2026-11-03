# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_041(Rule):
    """
    This rule checks that a file starts with a header comment, which holds the fields the required_fields option
    lists.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (DR10).

    A header of the same form in every file says what the file is, who owns it and how it is identified in
    configuration management. The header is the comments before the first line of code. A field is found as its name
    followed by a colon, such as :code:`Author:`, ignoring case. By default no field is required, only the header.

    **Violation**

    .. code-block:: vhdl

       library ieee;

    **Fix**

    .. code-block:: vhdl

       -- Title:  FIFO with a single clock
       -- Author: A. Designer
       library ieee;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add the file header"
        self.required_fields = []
        self.configuration.append("required_fields")

    def check(self, oModel, oFile):
        lHeader = []
        iFirstCode = None
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, model.parser.comment):
                lHeader.append(oToken.get_value() or "")
            elif not model.is_trivia(oToken):
                iFirstCode = iIndex
                break
        if iFirstCode is None:
            return
        if not lHeader:
            self.report(oFile, iFirstCode, "Start the file with a header comment")
            return
        sHeader = "\n".join(lHeader)
        for sField in self.required_fields:
            if not re.search(r"\b" + re.escape(str(sField)) + r"\s*:", sHeader, re.IGNORECASE):
                self.report(oFile, iFirstCode, f"Add the field {sField} to the file header")
