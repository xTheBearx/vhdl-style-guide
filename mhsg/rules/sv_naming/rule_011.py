# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_011(TreeRule, naming.Rule):
    """
    This rule checks that no name starts with VDD, VSS, VCC, GND or VREF, in any case, as the STARC guide asks
    (1.1.1.4). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic vdd_ok;

    **Fix**

    .. code-block:: systemverilog

       logic supply_ok;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.prefixes = ["VDD", "VSS", "VCC", "GND", "VREF"]
        self.configuration.append("prefixes")

    def problems(self, oFile):
        for _, oName in declared_names(oFile):
            if text(oName).upper().startswith(tuple(s.upper() for s in self.prefixes)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)}, which starts like a power net")
