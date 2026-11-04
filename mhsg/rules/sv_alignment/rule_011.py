# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import POLICIES, Rule
from mhsg.rules.sv_alignment.items import BODIES
from mhsg.rules.sv_tree import Problem, elements


class rule_011(Rule):
    """
    This rule aligns the colons of the packed dimensions that sv_alignment_010 aligns, by spaces after the opening
    bracket, as Verible's formatter does: [ 4:0] under [31:0]. Only the first packed dimension of a declaration is
    aligned, when it is a range such as [7:0]. By default it infers whether the author meant them aligned, as for the
    other alignment rules; **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       logic [31:0] data;
       logic [4:0]  count;

    **Fix**

    .. code-block:: systemverilog

       logic [31:0] data;
       logic [ 4:0] count;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Align the colons of the dimensions"
        # With the column of the dimensions, before the names
        self.subphase = 3
        self.minimum_spaces = 0
        self.widths = {}

    def alignment_groups(self, oFile):
        dIndex = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        self.widths = {}

        def row(oItem, oType):
            lDimensions = elements(getattr(oType, "dimensions", None) or [])
            oSpecifier = lDimensions[0].specifier if lDimensions else None
            oRange = getattr(oSpecifier, "selector", None) if oSpecifier is not None else None
            if oRange is None or oRange.kind.name != "SimpleRangeSelect":
                return False
            oFirst, oColon = oFile.token_at(oRange.left.getFirstToken()), oFile.token_at(oRange.range)
            if oFirst is None or oColon is None or id(oFirst) not in dIndex or id(oColon) not in dIndex:
                return False
            lBetween = oFile.lAllObjects[dIndex[id(oFirst)] : dIndex[id(oColon)]]
            sBetween = "".join(o.get_value() for o in lBetween)
            if "\n" in sBetween or "\t" in sBetween:
                return False
            self.widths[id(oFirst)] = len(sBetween)
            return (oItem, oRange.left.getFirstToken())

        for oList in oFile.nodes("AnsiPortList"):
            lRows = []
            for oPort in elements(oList.ports):
                if oPort.kind.name != "ImplicitAnsiPort":
                    lRows.append(None)
                elif oPort.header is None:
                    lRows.append(False)
                else:
                    lRows.append(row(oPort, getattr(oPort.header, "dataType", None)))
            yield lRows
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                lRows = []
                for oItem in getattr(oNode, sField, None) or []:
                    lRows.append(row(oItem, oItem.type) if oItem.kind.name in ("DataDeclaration", "NetDeclaration") else None)
                yield lRows

    def align(self, lRows):
        lRows = [t for t in lRows if id(t[1]) in self.widths]
        if len(lRows) < 2:
            return
        # Measured from each opening bracket, which sv_alignment_010 aligns
        iWidest = max(self.widths[id(oTarget)] for _, oTarget, _, _, _ in lRows)
        lWanted = [iWidest - self.widths[id(oTarget)] for _, oTarget, _, _, _ in lRows]
        sPolicy = self.policy if self.policy in POLICIES else "infer"
        if sPolicy == "infer":
            iExcess = max(iSpaces for _, _, _, _, iSpaces in lRows)
            if max(lWanted) <= 2:
                sPolicy = "align"
            elif iExcess <= 2:
                sPolicy = "flush_left"
            elif iExcess >= 4:
                sPolicy = "align"
            else:
                return
        for (oLeft, oTarget, _, _, iSpaces), iAligned in zip(lRows, lWanted):
            iWanted = iAligned if sPolicy == "align" else 0
            if iSpaces != iWanted:
                sWhat = f"Use {iWanted} space(s) after [ to align the colon" if sPolicy == "align" else f"Remove the spaces before {oTarget.get_value()}"
                yield Problem(oLeft, sWhat, oTarget, {"spaces": iWanted})
