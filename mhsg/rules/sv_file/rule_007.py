# -*- coding: utf-8 -*-

import fnmatch
import os

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks that a file holding a testbench, a module without ports, has a name matching one of
    **testbench_patterns**, file name patterns with :code:`*` and :code:`?`, by default :code:`*_tb.v`,
    :code:`*_tb.sv`, :code:`*_test.v`, :code:`*_test.sv` and :code:`*.vt`, as the STARC guide recommends (3.5.2.3). It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       // in fifo_check.sv
       module fifo_check;

    **Fix**

    .. code-block:: systemverilog

       // in fifo_tb.sv
       module fifo_tb;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.testbench_patterns = ["*_tb.v", "*_tb.sv", "*_test.v", "*_test.sv", "*.vt"]
        self.configuration.append("testbench_patterns")

    def problems(self, oFile):
        if not oFile.filename:
            return
        sName = os.path.basename(oFile.filename)
        if any(fnmatch.fnmatch(sName, s) for s in self.testbench_patterns):
            return
        for oModule in oFile.nodes("ModuleDeclaration"):
            oPorts = oModule.header.ports
            if oPorts is None or (hasattr(oPorts, "ports") and not list(elements(oPorts.ports))):
                oToken = oFile.token_at(oModule.header.name)
                if oToken is not None:
                    yield Problem(oToken, f"Name the file of the testbench {text(oModule.header.name)} like {', '.join(self.testbench_patterns)}")
