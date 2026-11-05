# -*- coding: utf-8 -*-
"""
The control pins of the flat design, clocks, asynchronous resets and tri-state enables, and the nets on them, for the
rules about how clocks and resets are made and where, such as design_032 to design_038.
"""

from mhsg.design import cdc, graph, netlist

CLOCK = "clock"
RESET = "reset"
TRISTATE = "tri-state enable"

TRISTATE_ENABLES = {"$tribuf": "EN", "$_TBUF_": "E"}
INVERTERS = {"$not", "$_NOT_"}


def control_pins(oFlat):
    """Yields (cell, port, kind) of each clock, asynchronous reset and tri-state enable pin of the flat design."""
    for oCell in oFlat.cells:
        if oCell.is_black_box():
            continue
        if cdc.is_clocked(oCell) and "CLK" in oCell.connections:
            yield oCell, "CLK", CLOCK
        elif oCell.type in netlist.LATCH_TYPES and "EN" in oCell.connections:
            yield oCell, "EN", CLOCK
        if oCell.type in graph.STATE_TYPES:
            for sPort in cdc.RESET_PORTS:
                if any(graph.is_variable(b) for b in oCell.connections.get(sPort, [])):
                    yield oCell, sPort, RESET
        sEnable = TRISTATE_ENABLES.get(oCell.type)
        if sEnable is not None and sEnable in oCell.connections:
            yield oCell, sEnable, TRISTATE


def clock_polarity(oAnalysis, oCell):
    """1 if a register takes its clock on the rising edge of the clock source, 0 on the falling edge."""
    _, lCells = oAnalysis.through_transparent(oCell.connections["CLK"][0])
    iInverted = sum(1 for o in lCells if o.type in INVERTERS)
    return (1 if oCell.parameter("CLK_POLARITY", 1) else 0) ^ (iInverted % 2)


def domain_cells(oAnalysis):
    """{Clock key: the registers and memory ports it clocks}, in the order of the flat design."""
    dReturn = {}
    for oCell in oAnalysis.flat.cells:
        oDomain = oAnalysis.cell_clock.get(id(oCell))
        if oDomain is not None:
            dReturn.setdefault(oDomain.key, []).append(oCell)
    return dReturn


def generated_clocks(oAnalysis):
    """
    The clocks made inside the design that clock registers: by a register, such as a divider, by logic, such as a gate
    or a multiplexer, or by a black box that derives a new clock, such as a PLL. Returns (Clock, generating cell).
    """
    lReturn = []
    for oDomain in oAnalysis.clocks.values():
        if oDomain.registers == 0 or oDomain.cell is None:
            continue
        if oDomain.kind in ("register", "logic"):
            lReturn.append((oDomain, oDomain.cell))
        elif oDomain.kind == "box":
            oRole = None
            for sPort, lNets in oDomain.cell.connections.items():
                if oDomain.net in lNets:
                    oRole = oAnalysis.box_role(oDomain.cell, sPort)
                    break
            if oRole is not None and oRole.kind == "clock_out" and oRole.relation in ("derived", "independent"):
                lReturn.append((oDomain, oDomain.cell))
    return lReturn


def reset_roots(oAnalysis):
    """{root net of an asynchronous reset: the registers it resets}."""
    dReturn = {}
    for oCell in oAnalysis.flat.cells:
        if not cdc.is_register(oCell):
            continue
        tSource = oAnalysis.reset_source(oCell)
        if tSource is None:
            continue
        dReturn.setdefault(oAnalysis.reset_root(tSource[1]), []).append(oCell)
    return dReturn


def generated_resets(oAnalysis):
    """The asynchronous resets made inside the design by a register or logic: (root net, generating cell, registers)."""
    lReturn = []
    for oRoot, lCells in reset_roots(oAnalysis).items():
        if not graph.is_variable(oRoot):
            continue
        tDriver = oAnalysis.flat.driver(oRoot)
        if tDriver is None or tDriver[0] is None or tDriver[0].is_black_box():
            continue
        lReturn.append((oRoot, tDriver[0], lCells))
    return lReturn


def instance_text(tPath):
    return "instance " + ".".join(tPath) if tPath else "the top-level module"


def locate(oContext, oFlat, oCell, sPort="Q"):
    """(file, line) of a cell, at the assignment of the signal it drives."""
    if oCell.is_black_box():
        return oContext.locate_cell(oCell)
    return oContext.locate_cell(oCell, oFlat.cell_name(oCell, sPort).split(".")[-1])
