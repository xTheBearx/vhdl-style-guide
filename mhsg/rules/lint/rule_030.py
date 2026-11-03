# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_030(Rule):
    """
    This rule checks that if, case and loop statements are not nested more deeply than a limit, four by default.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS20).

    Deep nesting makes code hard to review and to test, and builds long priority chains in hardware. The
    nesting_limit option sets the deepest level allowed.

    **Violation**

    .. code-block:: vhdl

       if a = '1' then
         if b = '1' then
           case c is
             when "00" =>
               if d = '1' then
                 for i in 0 to 3 loop    -- level 5
                   y(i) <= e(i);
                 end loop;
               end if;
             when others => null;
           end case;
         end if;
       end if;

    **Fix**

    .. code-block:: vhdl

       -- Move inner levels into a function, or combine conditions
    """

    def __init__(self):
        super().__init__()
        self.solution = "Reduce the nesting"
        self.nesting_limit = 4
        self.configuration.append("nesting_limit")

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                self.visit(oFile, oProcess.statements, 0)

    def visit(self, oFile, lStatements, iDepth):
        for oStatement in lStatements:
            if not isinstance(oStatement, (model.If, model.Case, model.Loop)):
                continue
            if iDepth + 1 > int(self.nesting_limit):
                self.report(oFile, oStatement.index, f"Nesting level {iDepth + 1} is deeper than the limit of {self.nesting_limit}")
                continue
            if isinstance(oStatement, model.If):
                for tBranch in oStatement.branches:
                    self.visit(oFile, tBranch[1], iDepth + 1)
            elif isinstance(oStatement, model.Case):
                for oAlternative in oStatement.alternatives:
                    self.visit(oFile, oAlternative.statements, iDepth + 1)
            else:
                self.visit(oFile, oStatement.statements, iDepth + 1)
