# -*- coding: utf-8 -*-

from mhsg.design import flat
from mhsg.design.rule import Finding, Rule, module_text

MEMORY_TYPES = {"$mem", "$mem_v2", "$memrd", "$memrd_v2", "$memwr", "$memwr_v2"}


class rule_030(Rule):
    """
    This rule reports memories that are not in the top-level module of the design.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it is a rule of the floor
              plan of ASICs.

    A memory at the top level is placed, tested and replaced by a memory macro more easily than one inside a block.
    Each module with memories is reported once.

    **Violation**

    A RAM inferred in a submodule.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Move the memory to the top-level module"

    def check_design(self, oContext):
        if oContext.netlist is None:
            return []
        sTop = flat.top_module(oContext.netlist)
        lReturn = []
        for sModule, dModule in sorted(oContext.netlist.modules.items()):
            if sModule == sTop:
                continue
            lCells = [s for s, d in dModule.get("cells", {}).items() if d.get("type") in MEMORY_TYPES]
            if not lCells:
                continue
            lMemories = sorted({str(dModule["cells"][s].get("parameters", {}).get("MEMID", "")).lstrip("\\") for s in lCells} - {""})
            # GHDL writes no locations on memory cells: then the module is located by its other cells
            sFile, iLine = self.locate(oContext, sModule, lCells + list(dModule.get("cells", {})))
            if sFile is None:
                # Else at an instance of the module
                for sParent, dParent in oContext.netlist.modules.items():
                    lInstances = [c for c, d in dParent.get("cells", {}).items() if d.get("type") == sModule]
                    if lInstances:
                        sFile, iLine = self.locate(oContext, sParent, lInstances)
                        if sFile is not None:
                            break
            sWhat = ", ".join(lMemories) if lMemories else "a memory"
            lReturn.append(Finding(sFile, iLine, f"Memory {sWhat} is in {module_text(sModule)}, not in the top-level module"))
        return lReturn
