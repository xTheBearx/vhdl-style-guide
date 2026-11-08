# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if, polarities
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

NAMES = ("IdentifierName", "IdentifierSelectName")


class rule_028(TreeRule, structure.Rule):
    """
    This rule checks that a reset is used with one polarity and one style throughout a file: active low or active
    high, and asynchronous or synchronous. The asynchronous resets of an edge triggered always block are the events of
    its event control that its first if tests, active low on negedge; its synchronous reset is a signal with a reset
    name, as for port_028, that the first if of a block with one clock tests. A reset that is active low in one block
    and active high in another, or both asynchronous and synchronous, behaves unexpectedly around reset. It is
    disabled by default; the do254 rule set enables it (SS13).

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) a <= 1'b0;
           else a <= d;

       always_ff @(posedge clk_i)
           if (rst_ni) b <= 1'b0;
           else b <= d;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) b <= 1'b0;
           else b <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dFirst = {}
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            for sName, bHigh, sStyle, oName in reset_uses(oBlock):
                oToken = oFile.token_at(oName)
                if oToken is None:
                    continue
                if sName not in dFirst:
                    dFirst[sName] = (bHigh, sStyle, oFile.line_of(oName.location.offset))
                    continue
                bFirstHigh, sFirstStyle, iLine = dFirst[sName]
                if (bHigh, sStyle) != (bFirstHigh, sFirstStyle):
                    sFirst = f"{'active high' if bFirstHigh else 'active low'} and {sFirstStyle}"
                    sThis = f"{'active high' if bHigh else 'active low'} and {sStyle}"
                    yield Problem(oToken, f"Use {sName} as on line {iLine}, {sFirst}, not {sThis}")


def reset_uses(oBlock):
    """(name, active high, asynchronous or synchronous, name token) of the resets of an edge triggered always block."""
    lClocks, lResets = clock_events(oBlock)
    if not lClocks:
        return []
    lReturn = []
    for oEvent in lResets:
        oName = oEvent.expr.getFirstToken()
        lReturn.append((text(oName), text(oEvent.edge) == "posedge", "asynchronous", oName))
    if lResets or len(lClocks) != 1:
        return lReturn
    oIf = first_if(oBlock.statement.statement)
    if oIf is None:
        return lReturn
    dTested = {}
    for oPattern in elements(oIf.predicate.conditions):
        dTested.update(polarities(oPattern.expr))
    for sName, bHigh in dTested.items():
        if clock_reset_rank(sName) == 1:
            oName = next((o.identifier for o in [oIf.predicate, *descendants(oIf.predicate)] if o.kind.name in NAMES and text(o.identifier) == sName), None)
            if oName is not None:
                lReturn.append((sName, bHigh, "synchronous", oName))
    return lReturn
