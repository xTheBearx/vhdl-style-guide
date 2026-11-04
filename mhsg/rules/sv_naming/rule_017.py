# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if, polarities
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_017(TreeRule, naming.Rule):
    """
    This rule checks that asynchronous resets that are active low, tested on negedge or with !, have names marking
    them so, matching **active_low_pattern**, a regular expression matched ignoring case, by default names ending in
    _n, _x, _b or _l, with i or o after it for ports, or such as rstn, as the STARC guide recommends (1.1.1.7). It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_i)
           if (!rst_i) q <= 1'b0;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) q <= 1'b0;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.active_low_pattern = ".*_(n|x|b|l)(i|o|io)?|.*(rst|reset|clr|clear|set)(n|b)(_(i|o|io))?"
        self.configuration.append("active_low_pattern")

    def problems(self, oFile):
        setDone = set()
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            _, lResets = clock_events(oBlock)
            if not lResets:
                continue
            dTested = {}
            oIf = first_if(oBlock.statement.statement)
            for oPattern in descendants(oIf.predicate) if oIf is not None else []:
                if oPattern.kind.name == "ConditionalPattern":
                    dTested.update(polarities(oPattern.expr))
            for oReset in lResets:
                oFirst = oReset.expr.getFirstToken()
                sName = text(oFirst)
                bLow = dTested.get(sName, text(oReset.edge) == "posedge") is False or text(oReset.edge) == "negedge"
                if not bLow or sName in setDone or re.fullmatch(self.active_low_pattern, sName, re.IGNORECASE):
                    continue
                setDone.add(sName)
                oToken = oFile.token_at(oFirst)
                if oToken is not None:
                    yield Problem(oToken, f"Mark the active low reset {sName} with a suffix such as _n")
