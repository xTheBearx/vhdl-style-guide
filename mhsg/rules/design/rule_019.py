# -*- coding: utf-8 -*-

import json
import os
import re
import subprocess
import tempfile

from mhsg.design import flat
from mhsg.design.rule import Finding, Rule

reLongest = re.compile(r"^Longest topological path in (\S+) \(length=(\d+)\):", re.MULTILINE)
reNode = re.compile(r"^\s+\d+: (.+?)(?: \(via .*\))?$")


class rule_019(Rule):
    """
    This rule reports the longest combinational path of the design after it is mapped to look-up tables of
    **lut_size** inputs, 6 by default, when it has more than **maximum_levels** levels, 8 by default.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: mapping takes longer than
              the other checks.

    design_007 counts the operators of a path before synthesis, which tells where a path is deep but not how deep it
    is in the device. This rule flattens the design, maps it with Yosys to look-up tables, and counts the tables on
    the longest path between registers, memories and the ports of the design, which is closer to the timing of the
    device. Mapping renames most signals, so the finding names the signal the path starts at, when it has a name, and
    is reported at the top of the design.

    **Violation**

    A chain of comparisons and multiplexers that maps to more look-up tables than allowed between two registers.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Split the path with a register"
        self.maximum_levels = 8
        self.lut_size = 6
        self.configuration.extend(["maximum_levels", "lut_size"])

    def check_design(self, oContext):
        if oContext.result is None or oContext.result.netlist is None or oContext.tools is None:
            return []
        dNetlist = oContext.result.netlist
        sTop = flat.top_module(oContext.netlist) if oContext.netlist is not None else None
        if sTop is None:
            return []
        tLongest = mapped_depth(oContext.tools, dNetlist, sTop, int(self.lut_size))
        if tLongest is None:
            return []
        iLevels, sStart = tLongest
        if iLevels <= int(self.maximum_levels):
            return []
        lCells = list(dNetlist["modules"][sTop].get("cells", {}))
        sFile, iLine = self.locate(oContext, sTop, lCells)
        sFrom = f", from {sStart}" if sStart else ""
        sMessage = f"Path of {iLevels} levels of {self.lut_size}-input look-up tables after mapping{sFrom}, more than {self.maximum_levels}"
        return [Finding(sFile, iLine, sMessage)]


def mapped_depth(oTools, dNetlist, sTop, iLutSize):
    """(levels, name of the signal it starts at or "") of the longest path after mapping to look-up tables, or None."""
    with tempfile.TemporaryDirectory(prefix="mhsg_mapped_") as sDirectory:
        sJson = os.path.join(sDirectory, "design.json")
        with open(sJson, "w", encoding="utf-8") as oFile:
            json.dump(dNetlist, oFile)
        sScript = f"read_json {sJson}; hierarchy -top {sTop}; flatten; synth -run coarse; opt; techmap; opt; abc -lut {iLutSize}; opt_clean; ltp -noff"
        oProcess = subprocess.run([oTools.yosys, "-p", sScript], capture_output=True, text=True, env=oTools.environment, check=False)
    if oProcess.returncode != 0:
        return None
    oMatch = None
    for oMatch in reLongest.finditer(oProcess.stdout):
        pass
    if oMatch is None:
        return None
    lLines = oProcess.stdout[oMatch.end() :].splitlines()[1:]
    oFirst = reNode.match(lLines[0]) if lLines else None
    sStart = oFirst.group(1).strip() if oFirst else ""
    sStart = "" if sStart.startswith("$") else sStart.lstrip("\\").replace(" [", "(").replace("]", ")")
    return int(oMatch.group(2)) - 1, sStart
