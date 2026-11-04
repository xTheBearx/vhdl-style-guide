# -*- coding: utf-8 -*-

import json
import os
import subprocess
import tempfile

from mhsg.design import flat
from mhsg.design.rule import Finding, Rule, module_text

# Transistors of the cells the design is mapped to, for gate equivalents of four transistors, a two-input NAND gate
TRANSISTORS = {
    "$_BUF_": 0,
    "$_NOT_": 2,
    "$_NAND_": 4,
    "$_NOR_": 4,
    "$_AND_": 6,
    "$_OR_": 6,
    "$_ANDNOT_": 6,
    "$_ORNOT_": 6,
    "$_AOI3_": 6,
    "$_OAI3_": 6,
    "$_AOI4_": 8,
    "$_OAI4_": 8,
    "$_NMUX_": 10,
    "$_MUX_": 12,
    "$_XOR_": 12,
    "$_XNOR_": 12,
    "$_TBUF_": 8,
}
FLIP_FLOP_TRANSISTORS = 24
LATCH_TRANSISTORS = 12


class rule_024(Rule):
    """
    This rule reports modules with more than **maximum_gates** gates, 40000 by default.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: mapping takes longer than
              the other checks.

    Synthesis and timing analysis work best on blocks of a limited size. This rule maps the design with Yosys to
    simple gates, without flattening it, and counts the logic of each module in two-input NAND gate equivalents:
    the logic of the module itself, not of the instances in it. Memories are not counted, as they become memory
    blocks of the device or the library.

    **Violation**

    An entity with more logic than allowed, instead of instances of smaller entities.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Split the module into smaller modules"
        self.maximum_gates = 40000
        self.configuration.append("maximum_gates")

    def check_design(self, oContext):
        if oContext.result is None or oContext.result.netlist is None or oContext.tools is None or oContext.netlist is None:
            return []
        sTop = flat.top_module(oContext.netlist)
        dGates = module_gates(oContext.tools, oContext.result.netlist, sTop)
        lReturn = []
        for sModule, dModule in sorted(oContext.netlist.modules.items()):
            iGates = dGates.get(sModule.lstrip("\\"))
            if iGates is None or iGates <= int(self.maximum_gates):
                continue
            sFile, iLine = self.locate(oContext, sModule, list(dModule.get("cells", {})))
            lReturn.append(Finding(sFile, iLine, f"Module {module_text(sModule)} has about {iGates} gates, more than {self.maximum_gates}"))
        return lReturn


def module_gates(oTools, dNetlist, sTop):
    """Returns {module name: gate equivalents of its own logic} after mapping the design to simple gates."""
    with tempfile.TemporaryDirectory(prefix="mhsg_gates_") as sDirectory:
        sJson = os.path.join(sDirectory, "design.json")
        sStatistics = os.path.join(sDirectory, "statistics.json")
        with open(sJson, "w", encoding="utf-8") as oFile:
            json.dump(dNetlist, oFile)
        sScript = (
            f"read_json {sJson}; hierarchy -top {sTop}; synth -run coarse; memory -nomap; opt -fast; techmap; opt -fast; "
            f"abc -g cmos3; opt_clean; tee -q -o {sStatistics} stat -json"
        )
        oProcess = subprocess.run([oTools.yosys, "-q", "-p", sScript], capture_output=True, text=True, env=oTools.environment, check=False)
        if oProcess.returncode != 0 or not os.path.exists(sStatistics):
            return {}
        with open(sStatistics, encoding="utf-8") as oFile:
            dStatistics = json.load(oFile)
    dReturn = {}
    for sModule, dModule in dStatistics.get("modules", {}).items():
        iTransistors = 0
        for sType, iCount in dModule.get("num_cells_by_type", {}).items():
            iTransistors += transistors(sType) * int(iCount)
        dReturn[sModule.lstrip("\\")] = (iTransistors + 3) // 4
    return dReturn


def transistors(sType):
    if sType in TRANSISTORS:
        return TRANSISTORS[sType]
    if sType.startswith(("$_DFF", "$_SDFF", "$_ALDFF", "$_DFFSR", "$_DFFE")):
        return FLIP_FLOP_TRANSISTORS
    if sType.startswith(("$_DLATCH", "$_SR_")):
        return LATCH_TRANSISTORS
    # Memories, instances of other modules and black boxes
    return 0
