# -*- coding: utf-8 -*-

from mhsg.design import flat, formal
from mhsg.design.rule import Finding, Rule, module_text


class rule_025(Rule):
    """
    This rule reports branches that can never be taken from reset: conditions never true or never false, and case
    choices never selected, proven with SymbiYosys.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs SymbiYosys, as in
              the YosysHQ OSS CAD Suite, and formal checks take longer than the other checks.

    Each branch, a value of the select input of a multiplexer, is first looked for in a search of **depth** clock
    cycles from reset, 20 by default, which takes at most **cover_timeout** seconds, 300 by default; the branches it
    reached by then count as reached. A branch the search does not reach gets a proof of its own, which takes at most
    **timeout** seconds, 60 by default, for at most **maximum_proofs** branches, 20 by default; the proofs run side by
    side, one per processor. A branch proven unreachable is reported. A branch neither reached nor proven is
    undecided, and reported when **report_undecided** is set. A branch that only selects unknown values, such as the
    others choice of a case statement that assigns :code:`'X'`, is how synthesis writes values never meant to occur,
    such as unused state encodings, and is not checked.

    The design starts from reset: the top inputs that drive asynchronous resets are active in the first cycle.
    **assumptions** hold top inputs at a value in every cycle, such as a test mode input, as in
    :code:`[test_mode=0]`. Black boxes are taken out, and their outputs can take any value. A branch is reported in
    every instance of its entity only when no instance takes it.

    **Violation**

    .. code-block:: vhdl

       -- count wraps at 5
       if count = 7 then
         alarm <= '1';
       end if;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Remove the branch, or fix the logic that should take it"
        self.depth = 20
        self.timeout = 60
        self.maximum_proofs = 20
        self.report_undecided = False
        self.cover_timeout = 300
        self.assumptions = []
        self.configuration.extend(["depth", "timeout", "cover_timeout", "maximum_proofs", "report_undecided", "assumptions"])

    def check_design(self, oContext):
        if oContext.result is None or oContext.result.netlist is None or oContext.netlist is None:
            return []
        sSby = formal.find_sby()
        sTop = flat.top_module(oContext.netlist)
        if sSby is None:
            sFile, iLine = self.top_location(oContext, sTop)
            return [Finding(sFile, iLine, "SymbiYosys (sby) is not installed: reachability is not checked")]
        lBranches, lUnchecked, sError = formal.reachability(
            sSby,
            oContext.result.netlist,
            sTop,
            oContext.flat(),
            set(oContext.netlist.black_boxes),
            int(self.depth),
            int(self.timeout),
            int(self.maximum_proofs),
            assumption_values(self.assumptions),
            int(self.cover_timeout),
        )
        lReturn = []
        if sError is not None:
            sFile, iLine = self.top_location(oContext, sTop)
            return [Finding(sFile, iLine, f"Reachability is not checked: {sError}")]
        for oBranch in lBranches:
            if oBranch.status == formal.UNREACHABLE:
                sMessage = f"Branch in {module_text(oBranch.module)} proven unreachable: {oBranch.describe()}"
            elif oBranch.status == formal.UNDECIDED and self.report_undecided:
                sMessage = (
                    f"Branch in {module_text(oBranch.module)} undecided: not taken within {self.depth} cycles, and not proven "
                    f"unreachable within {self.timeout} s"
                )
            else:
                continue
            sFile, iLine = self.locate(oContext, oBranch.module, oBranch.cells)
            lReturn.append(Finding(sFile, iLine, sMessage))
        if lUnchecked and self.report_undecided:
            sFile, iLine = self.top_location(oContext, sTop)
            lReturn.append(Finding(sFile, iLine, f"{len(lUnchecked)} branches not taken within {self.depth} cycles were not checked: more than maximum_proofs"))
        return lReturn

    def top_location(self, oContext, sTop):
        """The location of the top module, at its first located cell."""
        return self.locate(oContext, sTop, list(oContext.netlist.modules.get(sTop, {}).get("cells", {})))


def assumption_values(lAssumptions):
    """{top input: value} of assumptions written port=value, the value an integer such as 0, 5 or 0x1f."""
    dReturn = {}
    for sAssumption in lAssumptions or []:
        sPort, _, sValue = str(sAssumption).partition("=")
        dReturn[sPort.strip()] = int(sValue.strip() or "0", 0)
    return dReturn
