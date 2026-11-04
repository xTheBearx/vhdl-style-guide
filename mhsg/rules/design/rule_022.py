# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule

ASYNCHRONOUS_PORTS = {"ARST", "SET", "CLR"}
SYNCHRONOUS_PORTS = {"SRST"}
THROUGH_TYPES = {"$not", "$pos", "$buf", "$logic_not"}


class rule_022(Rule):
    """
    This rule reports reset signals used both as an asynchronous reset and as a synchronous reset.

    .. NOTE:: This is a design rule. It runs in design analysis.

    A reset that clears some registers at once and others at the next clock edge leaves the design in a state
    neither reset was meant for, for one clock cycle when the reset is asserted. A synchronous reset is a register
    loaded with a constant when the signal is asserted, in a clocked process.

    **Violation**

    .. code-block:: vhdl

       process (clk, reset) is
       begin
         if reset = '1' then
           a <= '0';
         elsif rising_edge(clk) then
           a <= d;
         end if;
       end process;

       process (clk) is
       begin
         if rising_edge(clk) then
           if reset = '1' then
             b <= '0';
       ...
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use the reset either as an asynchronous reset or as a synchronous reset"

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None:
            return []
        setAsynchronous = set()
        dSynchronous = {}
        for oCell in oFlat.cells:
            if not graph.is_state(oCell.cell):
                if oCell.type == "$mux" and loads_constant(oCell) and reaches_register(oFlat, oCell):
                    for oNet in oCell.connections.get("S", []):
                        dSynchronous.setdefault(source(oFlat, oNet), oCell)
                continue
            for sPort in ASYNCHRONOUS_PORTS:
                for oNet in oCell.connections.get(sPort, []):
                    setAsynchronous.add(source(oFlat, oNet))
            for sPort in SYNCHRONOUS_PORTS:
                for oNet in oCell.connections.get(sPort, []):
                    dSynchronous.setdefault(source(oFlat, oNet), oCell)
        lReturn = []
        for oNet in sorted(n for n in setAsynchronous & set(dSynchronous) if graph.is_variable(n)):
            sName = oFlat.net_name(oNet)
            sFile, iLine = oContext.locate_cell(dSynchronous[oNet])
            lReturn.append(Finding(sFile, iLine, f"Reset {sName} is used as an asynchronous reset and as a synchronous reset"))
        return lReturn


def source(oFlat, oNet):
    """Returns the net a net is a copy or an inversion of, following inverters and buffers."""
    setSeen = set()
    while graph.is_variable(oNet) and oNet not in setSeen:
        setSeen.add(oNet)
        tDriver = oFlat.driver(oNet)
        if tDriver is None or tDriver[0] is None or tDriver[0].type not in THROUGH_TYPES:
            break
        lInputs = tDriver[0].connections.get("A", [])
        if len(lInputs) != 1:
            break
        oNet = lInputs[0]
    return oNet


def loads_constant(oCell):
    """Returns whether one data input of a multiplexer is a constant 0 or 1, the value a reset loads."""
    for sPort in ("A", "B"):
        lBits = oCell.connections.get(sPort, [])
        if lBits and all(b in ("0", "1") for b in lBits):
            return True
    return False


def reaches_register(oFlat, oMux):
    """Returns whether the output of a multiplexer is the data input of a register, through multiplexers only."""
    lWork = [n for n in oMux.connections.get("Y", []) if graph.is_variable(n)]
    setSeen = set(lWork)
    while lWork:
        oNet = lWork.pop()
        for oReader, sPort, _ in oFlat.readers.get(oNet, []):
            if oReader is None:
                continue
            if graph.is_state(oReader.cell) and sPort == "D":
                return True
            if oReader.type in ("$mux", "$pmux") and sPort in ("A", "B"):
                for oOutput in oReader.connections.get("Y", []):
                    if graph.is_variable(oOutput) and oOutput not in setSeen:
                        setSeen.add(oOutput)
                        lWork.append(oOutput)
    return False
