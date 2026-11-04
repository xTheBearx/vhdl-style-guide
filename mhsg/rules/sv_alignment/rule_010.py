# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import BODIES, declared_dimension, port_dimension
from mhsg.rules.sv_alignment.rule_009 import row_or_skip
from mhsg.rules.sv_tree import elements


class rule_010(Rule):
    """
    This rule aligns the packed dimensions of the port declarations of a header, and of consecutive variable and net
    declarations, in a column, as Verible's formatter does. Declarations without a packed dimension are left out
    without ending the group. By default it infers whether the author meant them aligned or flush left; **policy**
    set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       logic [7:0] data;
       wire [3:0] strobe;

    **Fix**

    .. code-block:: systemverilog

       logic [7:0] data;
       wire  [3:0] strobe;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Align the column"
        # After the types of ports, before the names
        self.subphase = 3

    def alignment_groups(self, oFile):
        for oList in oFile.nodes("AnsiPortList"):
            yield [row_or_skip(o, port_dimension(o)) if o.kind.name == "ImplicitAnsiPort" else None for o in elements(oList.ports)]
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                lRows = []
                for oItem in getattr(oNode, sField, None) or []:
                    if oItem.kind.name in ("DataDeclaration", "NetDeclaration"):
                        lRows.append(row_or_skip(oItem, declared_dimension(oItem)))
                    else:
                        lRows.append(None)
                yield lRows
