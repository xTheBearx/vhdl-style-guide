# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_019(TreeRule, naming.Rule):
    """
    This rule checks that modules and instances are not named after the cells of the target library, listed in
    **cell_names**, compared ignoring case, as the STARC guide asks (1.1.1.10). The list is empty by default: give
    the cells of your library. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module AND2 (input logic a, b, output logic y);

    **Fix**

    .. code-block:: systemverilog

       module and_gate (input logic a, b, output logic y);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.cell_names = []
        self.configuration.append("cell_names")

    def problems(self, oFile):
        setCells = {str(s).lower() for s in self.cell_names}
        for sKind, oName in declared_names(oFile):
            if sKind in ("module", "instance") and text(oName).lower() in setCells:
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)}, the name of a cell of the library")
