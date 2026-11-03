# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_001(Rule):
    """
    This rule checks that a signal is assigned at most once in the same statement region of a process.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP2.

    A second assignment in the same sequence of statements overrides the first, which is usually a mistake.
    An assignment in a nested if or case statement, such as one that overrides a default value, is not a duplicate.
    Neither is an assignment after a wait statement or a procedure call, since time can pass there.

    **Violation**

    .. code-block:: vhdl

       if reset = '1' then
         beep <= '0';
         beep <= '1';
       end if;

    **Fix**

    .. code-block:: vhdl

       if reset = '1' then
         beep <= '0';
       end if;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the duplicate assignment"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                for lSequence in model.sequences(oProcess.statements):
                    dFirst = {}
                    for oStatement in lSequence:
                        if isinstance(oStatement, model.Other) and oStatement.kind in ("wait", "other", "call"):
                            # Time can pass at a wait statement, or in a procedure called here, so later assignments are new values
                            dFirst = {}
                            continue
                        if not isinstance(oStatement, model.Assignment) or oStatement.kind != "signal":
                            continue
                        if oStatement.target in dFirst:
                            self.report(
                                oFile,
                                oStatement.index,
                                f"Signal {oStatement.target} is also assigned on line {dFirst[oStatement.target]} in the same statement region",
                            )
                        else:
                            dFirst[oStatement.target] = oStatement.line
