# -*- coding: utf-8 -*-

from mhsg import language
from mhsg.lint.rule import Rule
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import descendants

IDENTIFIERS = ("IdentifierName", "IdentifierSelectName")
ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")


class rule_008(Rule):
    """
    This rule checks that the sensitivity list of a combinational always block names every signal and port of the
    file that the block reads. A missing signal makes simulation differ from synthesis; always_comb or always @*
    avoids the list altogether.

    .. NOTE:: This is a lint rule. It runs in lint mode.

    **Violation**

    .. code-block:: systemverilog

       always @(a_i) begin
           y = a_i & b_i;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           y = a_i & b_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.languages = (language.SYSTEMVERILOG,)
        self.solution = "Add the signals to the sensitivity list, or use always_comb"

    def check(self, oModel, oFile):
        if getattr(oFile, "dNodes", None) is None or oFile.syntax_errors:
            return
        setSignals = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("signal", "port")}
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        for oBlock in oFile.nodes("AlwaysBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            oControl = oStatement.timingControl
            if oControl.kind.name != "EventControlWithExpression":
                continue
            lEvents = [o for o in descendants(oControl) if o.kind.name == "SignalEventExpression"]
            if not lEvents or any(text(o.edge) for o in lEvents):
                continue
            setListed = {name_of(o.expr) for o in lEvents}
            lMissing = sorted(read_names(oStatement.statement) & setSignals - setListed)
            oToken = oFile.token_at(oControl.getFirstToken())
            if lMissing and oToken is not None and id(oToken) in dIndexes:
                self.report(oFile, dIndexes[id(oToken)], "Add " + ", ".join(lMissing) + " to the sensitivity list, or use always_comb")


def name_of(oExpression):
    oFirst = oExpression.getFirstToken() if oExpression is not None else None
    return text(oFirst)


def read_names(oStatement):
    """The names a statement reads: all names except the variables its assignments write."""
    if oStatement is None:
        return set()
    lNodes = [oStatement, *descendants(oStatement)]
    setTargets = set()
    for oNode in lNodes:
        if oNode.kind.name in ASSIGNMENTS and oNode.left.kind.name in IDENTIFIERS:
            setTargets.add(oNode.left.identifier.location.offset)
    return {text(o.identifier) for o in lNodes if o.kind.name in IDENTIFIERS and o.identifier.location.offset not in setTargets}
