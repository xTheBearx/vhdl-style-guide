# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import POLICIES, Rule
from mhsg.rules.sv_alignment.items import BODIES
from mhsg.rules.sv_tree import Problem, elements


class rule_011(Rule):
    """
    This rule aligns the packed dimensions of the declarations that sv_alignment_010 aligns, as Verible's formatter
    does: the text inside the brackets of each dimension is aligned right, by spaces after the opening bracket, so
    [ 4:0] goes under [31:0], and the brackets of the next dimension line up. Declarations without a dimension leave its
    column alone. By default it infers whether the author meant them aligned, as for the other alignment rules;
    **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       logic [31:0]       data;
       logic [4:0]        count;
       logic [7:0][3:0]   bytes;
       logic [15:0][31:0] words;

    **Fix**

    .. code-block:: systemverilog

       logic [31:0]       data;
       logic [ 4:0]       count;
       logic [ 7:0][ 3:0] bytes;
       logic [15:0][31:0] words;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Align the packed dimensions"
        # With the column of the dimensions, before the names
        self.subphase = 3
        self.minimum_spaces = 0
        self.widths = {}

    def alignment_groups(self, oFile):
        dIndex = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        self.widths = {}

        def row(oItem, oType, iDimension):
            """The row of a dimension of a declaration: (item, first token in the brackets), or False without one."""
            lDimensions = elements(getattr(oType, "dimensions", None) or [])
            if iDimension >= len(lDimensions):
                return False
            oDimension = lDimensions[iDimension]
            oSpecifier = getattr(oDimension, "specifier", None)
            if oSpecifier is None or getattr(oSpecifier, "selector", None) is None:
                return False
            oFirst, oClose = oFile.token_at(oSpecifier.getFirstToken()), oFile.token_at(oDimension.closeBracket)
            if oFirst is None or oClose is None or id(oFirst) not in dIndex or id(oClose) not in dIndex:
                return False
            sInside = "".join(o.get_value() for o in oFile.lAllObjects[dIndex[id(oFirst)] : dIndex[id(oClose)]])
            if "\n" in sInside or "\t" in sInside:
                return False
            self.widths[id(oFirst)] = len(sInside)
            return (oItem, oSpecifier.getFirstToken())

        def groups(lItems):
            """One group for each dimension: the rows of the items, None for an item that ends the group."""
            iDimensions = max((len(elements(getattr(oType, "dimensions", None) or [])) for _, oType in lItems if oType is not None), default=0)
            for iDimension in range(iDimensions):
                yield [row(oItem, oType, iDimension) if oType is not None else oItem for oItem, oType in lItems]

        for oList in oFile.nodes("AnsiPortList"):
            lItems = []
            for oPort in elements(oList.ports):
                if oPort.kind.name != "ImplicitAnsiPort":
                    lItems.append((None, None))
                elif oPort.header is None:
                    lItems.append((False, None))
                else:
                    lItems.append((oPort, getattr(oPort.header, "dataType", None) or False))
            yield from groups([(o, t) if t is not False else (False, None) for o, t in lItems])
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                lItems = []
                for oItem in getattr(oNode, sField, None) or []:
                    lItems.append((oItem, oItem.type) if oItem.kind.name in ("DataDeclaration", "NetDeclaration") else (None, None))
                yield from groups(lItems)

    def align(self, lRows):
        lRows = [t for t in lRows if id(t[1]) in self.widths]
        if len(lRows) < 2:
            return
        # Measured from each opening bracket, which sv_alignment_010 and the dimension before align
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
                sWhat = f"Use {iWanted} space(s) after [ to align the dimension" if sPolicy == "align" else f"Remove the spaces before {oTarget.get_value()}"
                yield Problem(oLeft, sWhat, oTarget, {"spaces": iWanted})
