# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_lint.rule_008 import Subprogram, read_names
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks that a function reads only its arguments, its own variables and constants, not the signals of
    the module, as the STARC guide asks (2.1.2.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic gate(input logic x);
           gate = x & enable;
       endfunction

    **Fix**

    .. code-block:: systemverilog

       function automatic logic gate(input logic x, input logic en);
           gate = x & en;
       endfunction
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setSignals = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("signal", "port")}
        for oNode in oFile.nodes("FunctionDeclaration"):
            oFunction = Subprogram(oNode)
            setRead = set()
            for oItem in oNode.items:
                setRead |= read_names(oItem, setSignals, {})
            lGlobal = sorted(s for s in setRead - oFunction.local if s in setSignals)
            if lGlobal:
                oToken = oFile.token_at(oNode.prototype.name.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Pass {', '.join(lGlobal)} to {oFunction.name} as arguments")
