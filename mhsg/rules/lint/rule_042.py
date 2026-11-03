# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_042(Rule):
    """
    This rule checks that comments make up a share of the lines of a file, 20 percent by default.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (DR11).

    The share is the number of lines with a comment over the number of lines that are not blank. The minimum_percent
    option sets the share required. A file below it is reported once, at its first line.

    **Violation**

    .. code-block:: vhdl

       architecture rtl of counter is
       begin
         count <= count + 1 when rising_edge(clk);
       end architecture rtl;

    **Fix**

    .. code-block:: vhdl

       -- Free-running counter of the clock cycles since power up
       architecture rtl of counter is
       begin
         -- Wraps around at its maximum
         count <= count + 1 when rising_edge(clk);
       end architecture rtl;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add comments"
        self.minimum_percent = 20
        self.configuration.append("minimum_percent")

    def check(self, oModel, oFile):
        setComment = set()
        setCode = set()
        iLine = 1
        iFirst = None
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, model.parser.carriage_return):
                iLine += 1
            elif isinstance(oToken, model.parser.comment):
                setComment.add(iLine)
            elif not model.is_trivia(oToken):
                setCode.add(iLine)
                iFirst = iIndex if iFirst is None else iFirst
        iLines = len(setComment | setCode)
        if iLines == 0 or iFirst is None:
            return
        fPercent = 100.0 * len(setComment) / iLines
        if fPercent < float(self.minimum_percent):
            self.report(oFile, iFirst, f"Comments are on {fPercent:.0f}% of the lines; add comments to reach {self.minimum_percent}%")
