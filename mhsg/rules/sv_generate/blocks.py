# -*- coding: utf-8 -*-
"""The begin-end blocks of generate constructs."""

GENERATE_PARENTS = ("LoopGenerate", "IfGenerate", "CaseGenerate")


def generate_blocks(oFile):
    """Yields the begin-end blocks of loop, if, else and case generate constructs."""
    for oBlock in oFile.nodes("GenerateBlock"):
        oParent = oBlock.parent
        while oParent is not None and oParent.kind.name in ("ElseClause", "StandardCaseItem", "DefaultCaseItem"):
            oParent = oParent.parent
        if oParent is not None and oParent.kind.name in GENERATE_PARENTS:
            yield oBlock


def label_of(oBlock):
    """The label token of a generate block, begin : name or name : begin, or None."""
    if oBlock.beginName is not None:
        return oBlock.beginName.name
    if oBlock.label is not None:
        return oBlock.label.name
    return None
