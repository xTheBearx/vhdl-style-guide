# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

BLOCKS = {
    "ModuleDeclaration": "module",
    "AlwaysBlock": "always block",
    "AlwaysFFBlock": "always block",
    "AlwaysCombBlock": "always block",
    "AlwaysLatchBlock": "always block",
}


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks that modules and always blocks carry a requirement tag, for traceability to the hardware
    requirements. It is disabled by default; the do254_plus rule set enables it (REQ).

    One of the comment lines directly above the module or always block, or the first comment inside it, must match
    the **pattern** option, a regular expression. The default accepts tags such as // REQ: HWR-123. Set the pattern
    to the tag format of your project.

    **Violation**

    .. code-block:: systemverilog

       // Output register
       always_ff @(posedge clk_i) begin

    **Fix**

    .. code-block:: systemverilog

       // Output register
       // REQ: HWR-123
       always_ff @(posedge clk_i) begin
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Add a requirement tag"
        self.pattern = r"\bREQ\s*:\s*\S+"
        self.configuration.append("pattern")

    def problems(self, oFile):
        oPattern = re.compile(self.pattern)
        lTokens = oFile.lAllObjects
        dIndexes = oFile.cached("indexes", lambda: {id(o): i for i, o in enumerate(lTokens)})
        for oNode in oFile.nodes(*BLOCKS):
            oFirst = oFile.token_at(oNode.getFirstToken())
            oLast = oFile.token_at(oNode.getLastToken())
            if oFirst is None or oLast is None or id(oFirst) not in dIndexes:
                continue
            iFirst, iLast = dIndexes[id(oFirst)], dIndexes.get(id(oLast), dIndexes[id(oFirst)])
            if not tagged(lTokens, iFirst, iLast, oPattern):
                yield Problem(oFirst, f"Add a requirement tag matching {self.pattern} to the {BLOCKS[oNode.kind.name]}")


def tagged(lTokens, iFirst, iLast, oPattern):
    """True if a comment line in the block directly above the token at iFirst, or the first comment up to iLast, matches."""
    for iIndex in range(iFirst - 1, -1, -1):
        oToken = lTokens[iIndex]
        if isinstance(oToken, (parser.whitespace, parser.carriage_return)):
            continue
        if not isinstance(oToken, parser.comment) or not starts_line(lTokens, iIndex):
            break
        if oPattern.search(oToken.get_value() or ""):
            return True
    for oToken in lTokens[iFirst + 1 : iLast + 1]:
        if isinstance(oToken, parser.comment):
            return bool(oPattern.search(oToken.get_value() or ""))
    return False


def starts_line(lTokens, iIndex):
    """True if the token at iIndex is the first on its line."""
    for iPrevious in range(iIndex - 1, -1, -1):
        oToken = lTokens[iPrevious]
        if isinstance(oToken, parser.whitespace):
            continue
        return isinstance(oToken, (parser.carriage_return, parser.blank_line))
    return True
