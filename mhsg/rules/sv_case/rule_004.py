# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that a case statement has at most **maximum_items** items, 200 by default, as the STARC guide
    asks (2.8.2.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    A case statement of 201 items.

    **Fix**

    Split the case statement, or use a memory or a function.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_items = 200
        self.configuration.append("maximum_items")

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            iItems = len(elements(oCase.items))
            if iItems > int(self.maximum_items):
                oToken = oFile.token_at(oCase.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Split the case statement: it has {iItems} items, more than {self.maximum_items}")
