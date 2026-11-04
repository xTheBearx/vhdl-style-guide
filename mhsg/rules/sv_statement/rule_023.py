# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import declared_names, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_023(TreeRule, structure.Rule):
    """
    This rule checks that an index that reads a signal is the signal alone, such as mem[addr], not an expression such
    as mem[addr + 1], as the STARC guide recommends (2.1.6.3). Indexes with only constants, parameters and loop
    variables are not checked. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = mem[addr + 1];

    **Fix**

    .. code-block:: systemverilog

       assign next_addr = addr + 1;
       assign y = mem[next_addr];
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setSignals = {text(o) for sKind, o in declared_names(oFile) if sKind in ("signal", "port")}
        for oSelect in oFile.nodes("ElementSelect"):
            oSelector = oSelect.selector
            if oSelector is None or oSelector.kind.name != "BitSelect" or oSelector.expr.kind.name in ("IdentifierName", "IdentifierSelectName"):
                continue
            lRead = [text(o.identifier) for o in descendants(oSelector.expr) if o.kind.name in ("IdentifierName", "IdentifierSelectName")]
            if any(s in setSignals for s in lRead):
                oToken = oFile.token_at(oSelector.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Index with a signal, not the expression {source(oSelector)}")
