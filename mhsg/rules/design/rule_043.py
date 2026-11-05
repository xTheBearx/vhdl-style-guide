# -*- coding: utf-8 -*-

import re

from mhsg.design import flat
from mhsg.design.rule import Finding, Rule, module_text
from mhsg.rules.design.rule_023 import port_location


class rule_043(Rule):
    """
    This rule checks the hierarchy identification of the modules of the design: each module name begins with an ID,
    matching **id_pattern** and followed by **separator**, such as A_top; the ID of a module instantiated in another
    extends the ID of that module, such as AB_ctrl under A_top; and the output ports of a module begin with its ID and
    the separator, such as A_data.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it.

    With IDs, a name says where in the hierarchy a module is, and an output port where its signal comes from, also in
    the netlist after synthesis. IDs are compared without regard to case; black boxes are not checked.

    **Violation**

    An entity B_ctrl instantiated in A_top, or an output port data of A_top.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.id_pattern = "[A-Za-z][A-Za-z0-9]*"
        self.separator = "_"
        self.configuration.extend(["id_pattern", "separator"])
        self.solution = "Name modules and output ports after the hierarchy IDs"

    def hierarchy_id(self, sModule):
        """The ID a module name begins with, or None."""
        sName = module_text(sModule)
        sSeparator = str(self.separator)
        if sSeparator not in sName:
            return None
        sId = sName.split(sSeparator)[0]
        return sId if re.fullmatch(str(self.id_pattern), sId) else None

    def check_design(self, oContext):
        if oContext.netlist is None:
            return []
        dModules = oContext.netlist.modules
        sTop = flat.top_module(oContext.netlist)
        lReturn = []
        # The modules of the hierarchy from the top, each with the module that instantiates it first and the instance
        dParents = {sTop: (None, None)}
        lWork = [sTop]
        while lWork:
            sModule = lWork.pop(0)
            for sCell, dCell in sorted(dModules[sModule].get("cells", {}).items()):
                sType = dCell.get("type")
                if sType in dModules and sType not in dParents:
                    dParents[sType] = (sModule, sCell)
                    lWork.append(sType)
        for sModule, (sParent, sCell) in dParents.items():
            sFile, iLine = self.module_location(oContext, sModule, sParent, sCell)
            sId = self.hierarchy_id(sModule)
            if sId is None:
                lReturn.append(Finding(sFile, iLine, f"Module {module_text(sModule)} does not begin with a hierarchy ID and {self.separator}"))
                continue
            sParentId = self.hierarchy_id(sParent) if sParent is not None else None
            if sParentId is not None and not (sId.lower().startswith(sParentId.lower()) and len(sId) > len(sParentId)):
                sMessage = f"Hierarchy ID {sId} of {module_text(sModule)} does not extend ID {sParentId} of {module_text(sParent)}"
                lReturn.append(Finding(sFile, iLine, sMessage))
            sPrefix = sId + str(self.separator)
            lPorts = []
            for sPort, dPort in sorted(dModules[sModule].get("ports", {}).items()):
                sName = sPort.lstrip("\\").split(".")[0]
                if dPort.get("direction") == "output" and not sName.lower().startswith(sPrefix.lower()) and sName not in [s for s, _ in lPorts]:
                    lPorts.append((sName, sPort))
            if lPorts:
                sPortFile, iPortLine = port_location(oContext, sModule, lPorts[0][1])
                if sPortFile is None:
                    sPortFile, iPortLine = sFile, iLine
                sNames = ", ".join(s for s, _ in lPorts[:4]) + (f" and {len(lPorts) - 4} more" if len(lPorts) > 4 else "")
                sWhat = "Output port" if len(lPorts) == 1 else "Output ports"
                lReturn.append(
                    Finding(sPortFile, iPortLine, f"{sWhat} {sNames} of {module_text(sModule)} do{'es' if len(lPorts) == 1 else ''} not begin with {sPrefix}"),
                )
        return lReturn

    def module_location(self, oContext, sModule, sParent, sCell):
        """At the first cell of a module with a location; for a module of instances only, at its instance in its parent."""
        sFile, iLine = self.locate(oContext, sModule, sorted(oContext.netlist.modules[sModule].get("cells", {})))
        if sFile is None and sParent is not None:
            sFile, iLine = self.locate(oContext, sParent, [sCell])
        return sFile, iLine
