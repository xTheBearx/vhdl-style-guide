# -*- coding: utf-8 -*-

import os

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_021(Rule):
    """
    This rule checks that a file holds one entity, named like the file.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    One entity and its architectures per file, in a file named after the entity, makes a design easy to navigate and review.
    Files without an entity, such as packages, are not checked.

    **Violation**

    A file :code:`top.vhd` that declares the entities :code:`fifo` and :code:`ram`.

    **Fix**

    The entities in files :code:`fifo.vhd` and :code:`ram.vhd`.
    """

    def __init__(self):
        super().__init__()
        self.solution = "One entity per file, named after it"

    def check(self, oModel, oFile):
        lEntities = []
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if model.kind(oToken) == ("entity_declaration", "identifier"):
                lEntities.append((oToken.get_value(), iIndex))
        for sName, iIndex in lEntities[1:]:
            self.report(oFile, iIndex, f"Move entity {sName} to a file of its own; this file already declares {lEntities[0][0]}")
        sFileName = getattr(oFile, "filename", None)
        if lEntities and sFileName:
            sBase = os.path.splitext(os.path.basename(sFileName))[0]
            if sBase.lower() != lEntities[0][0].lower():
                self.report(oFile, lEntities[0][1], f"Name the file after entity {lEntities[0][0]}")
