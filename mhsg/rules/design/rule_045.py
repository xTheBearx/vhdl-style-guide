# -*- coding: utf-8 -*-

from mhsg.design import cdc, graph
from mhsg.design.rule import Finding, Rule


class rule_045(Rule):
    """
    This rule reports register to register paths whose logic spans more than **maximum_blocks** blocks, 2 by default:
    the instances that hold the source registers, the logic between them and the register at the end.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it is meant for designs
              whose blocks are synthesized and timed on their own.

    A path through the logic of several blocks is timed only when they are put together, and changing one block
    changes the timing of the others. Registered outputs, or inputs, keep each path within two blocks. The top-level
    module counts as a block when it holds logic; instances that only pass signals through do not count. For
    speed-critical paths, STARC asks for two blocks, or three with speed problems, which **maximum_blocks** sets.

    **Violation**

    An output of block u_a computed by logic from its registers, read by logic in block u_b before a register of u_c.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.maximum_blocks = 2
        self.configuration.append("maximum_blocks")
        self.solution = "Register the outputs or inputs of the blocks, so each path stays within two blocks"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        self._dBlocks = {}
        dFound = {}
        for oCell in oFlat.cells:
            if not cdc.is_register(oCell):
                continue
            setBlocks = {oCell.path}
            for sPort, lNets in oCell.connections.items():
                if sPort in cdc.CONTROL_PORTS or oFlat.direction(oCell, sPort) != "input":
                    continue
                for oNet in lNets:
                    setBlocks |= self.blocks(oAnalysis, oNet)
            if len(setBlocks) > int(self.maximum_blocks):
                dFound.setdefault(frozenset(setBlocks), []).append(oCell)
        lReturn = []
        for setBlocks, lCells in dFound.items():
            lCells.sort(key=oFlat.cell_name)
            sNames = ", ".join(sorted(".".join(t) if t else "the top level" for t in setBlocks))
            sMore = f" and {len(lCells) - 1} more register{'s' if len(lCells) > 2 else ''}" if len(lCells) > 1 else ""
            sName = oFlat.cell_name(lCells[0])
            sFile, iLine = oContext.locate_cell(lCells[0], sName.split(".")[-1])
            lReturn.append(Finding(sFile, iLine, f"Paths into {sName}{sMore} span {len(setBlocks)} blocks: {sNames}"))
        return sorted(lReturn, key=lambda o: (o.file or "", o.line, o.message))

    def blocks(self, oAnalysis, oNet):
        """The instance paths of the logic that drives a net, back to registers, memories, black boxes and top inputs."""
        if not graph.is_variable(oNet):
            return frozenset()
        if oNet in self._dBlocks:
            return self._dBlocks[oNet]
        lStack = [(oNet, False)]
        setVisiting = set()
        while lStack:
            oCurrent, bDone = lStack.pop()
            if oCurrent in self._dBlocks or (not bDone and oCurrent in setVisiting):
                continue
            tDriver = oAnalysis.flat.driver(oCurrent)
            if tDriver is None or tDriver[0] is None:
                self._dBlocks[oCurrent] = frozenset()
                continue
            oCell, sPort, iIndex = tDriver
            if oCell.is_black_box() or cdc.is_clocked(oCell) or oCell.type in graph.STATE_TYPES or oCell.type in cdc.MEMORY_READ_TYPES:
                self._dBlocks[oCurrent] = frozenset([oCell.path])
                continue
            lInputs = oAnalysis.comb_inputs(oCell, sPort, iIndex)
            if not bDone:
                setVisiting.add(oCurrent)
                lStack.append((oCurrent, True))
                lStack.extend((b, False) for b in lInputs if b not in self._dBlocks and b not in setVisiting)
                continue
            setResult = {oCell.path}
            for oInput in lInputs:
                setResult |= self._dBlocks.get(oInput, frozenset())
            self._dBlocks[oCurrent] = frozenset(setResult)
        return self._dBlocks[oNet]
