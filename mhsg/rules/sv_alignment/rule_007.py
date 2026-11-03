# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule


class rule_007(Rule):
    """
    This rule aligns the statements of case items written on the line of their item in a column, as Verible's
    formatter does. By default it infers whether the author meant them aligned or flush left; **policy** set to
    align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       Idle: state_d = Busy;
       default: state_d = Idle;

    **Fix**

    .. code-block:: systemverilog

       Idle:    state_d = Busy;
       default: state_d = Idle;
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 1
        self.solution = "Align the column"
        # Before the other alignments: aligning the statements of case items moves what follows them
        self.subphase = 1

    def alignment_groups(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            yield [
                (o, o.clause.getFirstToken()) if o.kind.name in ("StandardCaseItem", "DefaultCaseItem") and o.clause is not None else None for o in oCase.items
            ]
