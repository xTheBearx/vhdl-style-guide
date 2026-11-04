# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_013(TreeRule, structure.Rule):
    """
    This rule checks that a text macro defined inside a module is undefined with an undef directive before the end
    of the module, so it is used only there, as the STARC guide recommends (1.1.4.4). It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo;
           `define DEPTH 4
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module fifo;
           `define DEPTH 4
           `undef DEPTH
       endmodule
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lUndefined = [(text(o.name), o.name.location.offset) for o in oFile.nodes("UndefDirective") if o.name is not None]
        for oModule in oFile.nodes("ModuleDeclaration"):
            iStart, iEnd = oModule.getFirstToken().location.offset, oModule.getLastToken().location.offset
            for oDefine in oFile.nodes("DefineDirective"):
                iOffset = oDefine.name.location.offset
                if not iStart < iOffset < iEnd:
                    continue
                if not any(s == text(oDefine.name) and iOffset < i < iEnd for s, i in lUndefined):
                    oToken = oFile.token_at(oDefine.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Undefine {text(oDefine.name)} with an undef directive before the end of the module")
