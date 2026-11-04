# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule

TASKS = ("$display", "$write", "$monitor", "$strobe", "$finish", "$stop", "$fopen", "$fclose", "$fdisplay", "$fwrite", "$readmemh", "$readmemb")


class rule_033(TreeRule, structure.Rule):
    """
    This rule checks that system tasks for simulation, such as $display or $finish, in modules with ports are between
    translate_off and translate_on pragma comments, as the STARC guide asks (4.3.11.3). It is disabled by default;
    the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) if (err) $display("error");

    **Fix**

    .. code-block:: systemverilog

       // synopsys translate_off
       always_ff @(posedge clk_i) if (err) $display("error");
       // synopsys translate_on
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFenced = fenced_lines(oFile)
        for oNode in oFile.nodes("InvocationExpression"):
            if oNode.left is None or oNode.left.kind.name != "SystemName" or text(oNode.left.systemIdentifier) not in TASKS:
                continue
            oModule = next(
                (
                    o
                    for o in oFile.nodes("ModuleDeclaration")
                    if o.getFirstToken().location.offset <= oNode.getFirstToken().location.offset <= o.getLastToken().location.offset
                ),
                None,
            )
            if oModule is None or oModule.header.ports is None or not inside(oNode, "ModuleDeclaration"):
                continue
            iLine = oFile.line_of(oNode.getFirstToken().location.offset)
            if any(iStart < iLine < iEnd for iStart, iEnd in lFenced):
                continue
            oToken = oFile.token_at(oNode.left.systemIdentifier)
            if oToken is not None:
                yield Problem(oToken, f"Put {text(oNode.left.systemIdentifier)} between translate_off and translate_on pragmas")


def fenced_lines(oFile):
    """(line of translate_off, line of translate_on) of each region between those pragma comments."""
    lReturn = []
    iStart = None
    for iIndex, oToken in enumerate(oFile.lAllObjects):
        if not isinstance(oToken, parser.comment):
            continue
        sText = oToken.get_value().lower()
        if re.search(r"\btranslate_off\b", sText) and iStart is None:
            iStart = oFile.oTokenMap.get_line_number_of_index(iIndex)
        elif re.search(r"\btranslate_on\b", sText) and iStart is not None:
            lReturn.append((iStart, oFile.oTokenMap.get_line_number_of_index(iIndex)))
            iStart = None
    if iStart is not None:
        lReturn.append((iStart, float("inf")))
    return lReturn
