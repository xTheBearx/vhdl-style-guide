# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_022(Rule):
    """
    This rule checks for variables in a clocked process that are read before they are written.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    Such a variable keeps its value from the previous clock edge, so synthesis makes it a register.
    That register is easy to overlook, because it has no signal.
    Write the variable before reading it, or make the register a signal.

    **Violation**

    .. code-block:: vhdl

       process (clk) is
         variable count : natural range 0 to 15;
       begin
         if rising_edge(clk) then
           count := count + 1;
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (clk) is
       begin
         if rising_edge(clk) then
           count_r <= count_r + 1;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Write the variable before reading it"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if oProcess.clock is None or not oProcess.variables:
                    continue
                lReported = []
                visit(oProcess.clock.clock_branch, set(), oProcess.variables, lReported)
                for sName, iIndex in lReported:
                    self.report(
                        oFile,
                        iIndex,
                        f"Variable {sName} is read before it is written, so it holds its value from the previous clock edge like a register",
                    )


def visit(lStatements, setAssigned, setVariables, lReported):
    """Walks statements in order, reporting variables read before they are assigned, and returns the variables assigned on every path."""
    setAssigned = set(setAssigned)
    for oStatement in lStatements:
        if isinstance(oStatement, model.Other) and oStatement.kind == "call":
            # A variable given to a procedure may be an out parameter, which the procedure assigns
            setAssigned.update(s for s in oStatement.reads if s.split(".")[0] in setVariables)
        elif isinstance(oStatement, (model.Assignment, model.Other)):
            check_reads(oStatement.reads, oStatement.index, setAssigned, setVariables, lReported)
            if isinstance(oStatement, model.Assignment) and oStatement.kind == "variable":
                setAssigned.add(oStatement.covers())
        elif isinstance(oStatement, model.If):
            lResults = []
            for tBranch in oStatement.branches:
                check_reads(model.names(tBranch[0] or []), tBranch[3], setAssigned, setVariables, lReported)
                lResults.append(visit(tBranch[1], setAssigned, setVariables, lReported))
            if oStatement.has_else:
                setAssigned |= model.common(lResults)
        elif isinstance(oStatement, model.Case):
            check_reads(model.names(oStatement.selector), oStatement.index, setAssigned, setVariables, lReported)
            lResults = [visit(o.statements, setAssigned, setVariables, lReported) for o in oStatement.alternatives]
            if lResults:
                setAssigned |= model.common(lResults)
        elif isinstance(oStatement, model.Loop):
            check_reads(model.names(oStatement.header), oStatement.index, setAssigned, setVariables, lReported)
            # The parameter of a for loop hides a variable of the same name inside the loop
            visit(oStatement.statements, setAssigned | ({oStatement.parameter} if oStatement.parameter else set()), setVariables, lReported)
            # An element assignment indexed by the parameter of a for loop, such as v(i) := ..., assigns every element
            if oStatement.parameter:
                for oAssignment in model.assignments(oStatement.statements, "variable"):
                    if re.search(r"\(\s*" + re.escape(oStatement.parameter) + r"\s*\)", oAssignment.target):
                        setAssigned.add(oAssignment.base)
    return setAssigned


def check_reads(lReads, iIndex, setAssigned, setVariables, lReported):
    for sRead in lReads:
        sName = sRead.split(".")[0]
        if sName in setVariables and not model.covered(sRead, setAssigned) and sName not in [s for s, i in lReported]:
            lReported.append((sName, iIndex))
