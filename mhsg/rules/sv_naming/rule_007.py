# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_007(TreeRule, naming.Rule):
    """
    This rule checks that no parameter name starts with disable; name it after what it enables, as Verible's
    positive-meaning-parameter-name rule does.

    **Violation**

    .. code-block:: systemverilog

       parameter bit DisableParity = 1'b0;

    **Fix**

    .. code-block:: systemverilog

       parameter bit EnableParity = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for _, oName in names_of_kinds(oFile, ("parameter", "localparam")):
            if text(oName).lower().startswith("disable"):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)} after what it enables")
