# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_018(Rule):
    """
    This rule checks that entities and processes carry a requirement tag, for traceability to the hardware requirements.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    One of the comment lines directly above the entity or process, or the first comment inside it, must match the
    :code:`pattern` option, a regular expression. The default accepts tags such as :code:`-- REQ: HWR-123`.
    Set the pattern to the tag format of your project.

    **Violation**

    .. code-block:: vhdl

       -- Output register
       proc_out : process (clk) is

    **Fix**

    .. code-block:: vhdl

       -- Output register
       -- REQ: HWR-123
       proc_out : process (clk) is
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a requirement tag"
        self.pattern = r"\bREQ\s*:\s*\S+"
        self.configuration.append("pattern")

    def check(self, oModel, oFile):
        oPattern = re.compile(self.pattern)
        lTokens = oFile.lAllObjects
        for iIndex, oToken in enumerate(lTokens):
            tKind = model.kind(oToken)
            if tKind == ("entity_declaration", "entity_keyword"):
                sWhat = "entity"
            elif tKind == ("process_statement", "process_label") or (tKind == ("process_statement", "process_keyword") and not labelled(lTokens, iIndex)):
                sWhat = "process"
            else:
                continue
            if not tagged(lTokens, iIndex, oPattern):
                self.report(oFile, iIndex, f"Add a requirement tag matching {self.pattern} to the {sWhat}")


def labelled(lTokens, iIndex):
    for iPrevious in range(iIndex - 1, -1, -1):
        if not model.is_trivia(lTokens[iPrevious]):
            return model.kind(lTokens[iPrevious]) == ("process_statement", "label_colon")
    return False


def tagged(lTokens, iIndex, oPattern):
    """Returns True if a comment in the block directly above the token, or the first comment after it, matches the pattern."""
    for iPrevious in range(iIndex - 1, -1, -1):
        oToken = lTokens[iPrevious]
        if isinstance(oToken, parser.comment):
            if oPattern.search(oToken.get_value() or ""):
                return True
        elif isinstance(oToken, parser.blank_line):
            break
        elif not model.is_trivia(oToken):
            break
    for oToken in lTokens[iIndex + 1 :]:
        if isinstance(oToken, parser.comment):
            return bool(oPattern.search(oToken.get_value() or ""))
        if model.kind(oToken)[1] in ("begin_keyword", "end_keyword"):
            return False
    return False
