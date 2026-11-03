# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule

# (module, class) of the token that starts each construct, and what to report
CONSTRUCTS = {
    ("wait_statement", "wait_keyword"): "wait statement",
    ("waveform_element", "after_keyword"): "after delay",
    ("delay_mechanism", "transport_keyword"): "transport delay",
    ("variable_declaration", "shared_keyword"): "shared variable",
    ("file_declaration", "file_keyword"): "file declaration",
    ("access_type_definition", "access_keyword"): "access type",
}


class rule_014(Rule):
    """
    This rule checks for constructs that only simulation supports, in code meant for synthesis.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    Wait statements, after delays, transport delays, shared variables, files, access types and signals or variables of type
    real are ignored or rejected by synthesis, so simulation and hardware can behave differently.
    Constants of type real are allowed, since they are evaluated at elaboration.
    Run lint mode on synthesizable code only, or disable this rule for testbenches.

    **Violation**

    .. code-block:: vhdl

       q <= d after 1 ns;

    **Fix**

    .. code-block:: vhdl

       q <= d;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the simulation-only construct"

    def check(self, oModel, oFile):
        bType = False
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            if tKind in CONSTRUCTS:
                self.report(oFile, iIndex, f"Remove the {CONSTRUCTS[tKind]}; synthesis does not support it")
            elif tKind[0] in ("signal_declaration", "variable_declaration") and tKind[1] == "colon":
                bType = True
            elif bType and tKind == ("type_mark", "name"):
                if (oToken.get_value() or "").lower() == "real":
                    self.report(oFile, iIndex, "Replace the real type with a fixed point or integer type; synthesis does not support it")
                bType = False
