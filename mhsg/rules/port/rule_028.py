# -*- coding: utf-8 -*-

import fnmatch

from mhsg import parser, violation
from mhsg.rule_group import structure
from mhsg.rules import port_clause_utils
from mhsg.vhdlFile import utils

lKeys = ["clock_reset", "direction", "name"]


class rule_028(structure.Rule):
    """
    This rule checks the order of port declarations.

    .. NOTE:: This rule is disabled by default.

    The order is set by these options:

    * :code:`order`: the sort keys, most important first.
      The keys are :code:`clock_reset`, :code:`direction` and :code:`name`.
      The default is :code:`[clock_reset, direction, name]`.
    * :code:`clock_patterns` and :code:`reset_patterns`: name patterns, with :code:`*` as a wildcard, for the :code:`clock_reset` key.
      Clocks come first, then resets, then the other ports.
    * :code:`direction_order`: the order of the modes for the :code:`direction` key.
      The default is :code:`[in, inout, out, buffer, linkage]`.
      A port without a mode is an :code:`in` port.
    * :code:`sort_within_sections`: :code:`yes` (default) sorts each group of ports separated by a blank line or comment line on its own.
      :code:`no` sorts the whole port list.

    Names are compared ignoring case.
    A declaration with several names is sorted by its first name.

    By default the rule only reports the expected order.
    Moving the ports of an entity changes what a direct instantiation with positional association connects to.
    With :code:`move_ports` set to :code:`when_safe`, the ports of an entity are moved if no file of the run instantiates it directly with positional association.
    A top-level entity, which is not instantiated in the run, is always moved.
    Instances in files that are not part of the run are not checked, and input from stdin is never moved.
    Ports of component declarations are only reported, because moving them changes what positional instances of the component connect to.
    Ports are only moved if each declaration is on a line of its own; comments at the end of a line move with their port.

    **Violation**

    .. code-block:: vhdl

       port (
         data_o : out std_logic;
         clk    : in  std_logic;
         a_i    : in  std_logic
       );

    **Fix**

    .. code-block:: vhdl

       port (
         clk    : in  std_logic;
         a_i    : in  std_logic;
         data_o : out std_logic
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Order ports"
        self.phase = 1
        self.subphase = 5
        self.disable = True
        self.order = list(lKeys)
        self.configuration.append("order")
        self.direction_order = ["in", "inout", "out", "buffer", "linkage"]
        self.configuration.append("direction_order")
        self.clock_patterns = ["clk", "clock", "*_clk", "clk_*", "*_clock", "clock_*"]
        self.configuration.append("clock_patterns")
        self.reset_patterns = ["rst", "rstn", "reset", "resetn", "*_rst", "rst_*", "*_rstn", "*_reset", "reset_*", "*_resetn"]
        self.configuration.append("reset_patterns")
        self.sort_within_sections = "yes"
        self.configuration.append("sort_within_sections")
        self.move_ports = "never"
        self.configuration.append("move_ports")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        bWithinSections = utils.convert_yes_no_option_to_boolean(self.sort_within_sections)
        lPositional = getattr(oFile.configuration, "project_positional_entities", None)
        lReturn = []
        for oToi in port_clause_utils.get_port_clauses(oFile):
            lElements = port_clause_utils.get_elements(oToi)
            sKind, sName = port_clause_utils.get_context(oFile, oToi)
            if bWithinSections:
                lGroups = port_clause_utils.get_sections(lElements)
            else:
                lGroups = [lElements]
            for lGroup in lGroups:
                lExpected = sorted(lGroup, key=self._sort_key)
                if lExpected == lGroup:
                    continue
                sReason = self._reason_not_moved(sKind, sName, lPositional, lGroup, lElements, bWithinSections)
                lReturn.append(create_toi(oToi, lGroup, lExpected, sReason))
        return lReturn

    def _sort_key(self, dElement):
        lReturn = []
        for sKey in self.order:
            if sKey == "clock_reset":
                lReturn.append(self._clock_reset_rank(dElement["names"][0]))
            elif sKey == "direction":
                lReturn.append(direction_rank(dElement["mode"], self.direction_order))
            elif sKey == "name":
                lReturn.append(dElement["names"][0].lower())
        return lReturn

    def _clock_reset_rank(self, sName):
        if matches_any(sName, self.clock_patterns):
            return 0
        if matches_any(sName, self.reset_patterns):
            return 1
        return 2

    def _reason_not_moved(self, sKind, sName, lPositional, lGroup, lElements, bWithinSections):
        if self.move_ports != "when_safe":
            return "move_ports is never"
        if sKind == "component":
            return "ports of component declarations are not moved"
        if sKind != "entity":
            return "only ports of entities are moved"
        if lPositional is None:
            return "the instances of the entity are not known"
        if sName.lower() in lPositional:
            return "the entity is instantiated with positional association"
        if not bWithinSections and len(port_clause_utils.get_sections(lElements)) > 1:
            return "the ports are separated by blank lines or comments"
        for dElement in lGroup:
            if not dElement["single_line"] or dElement["close_on_same_line"]:
                return "a port declaration is not on a line of its own"
        return None

    def _analyze(self, lToi):
        for oToi in lToi:
            dAction = oToi.get_meta_data("action")
            sSolution = "Order ports: " + ", ".join(dAction["order"])
            if dAction["reason"] is not None:
                sSolution += " (not moved: " + dAction["reason"] + ")"
            oViolation = violation.New(oToi.get_meta_data("line"), oToi, sSolution)
            oViolation.set_action(dAction)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        dAction = oViolation.get_action()
        if dAction["reason"] is not None:
            return
        oViolation.set_tokens(reorder(oViolation.get_tokens(), dAction["slots"], dAction["sources"]))


def direction_rank(sMode, lDirectionOrder):
    lOrder = [sDirection.lower() for sDirection in lDirectionOrder]
    if sMode in lOrder:
        return lOrder.index(sMode)
    return len(lOrder)


def matches_any(sName, lPatterns):
    return any(fnmatch.fnmatchcase(sName.lower(), sPattern.lower()) for sPattern in lPatterns)


def create_toi(oToi, lGroup, lExpected, sReason):
    """
    Returns the tokens of a group of ports.  Each port's position in the group is a slot:
    the declaration in the first slot is replaced by the first declaration of the expected order, and so on.
    """
    iStart = lGroup[0]["start"]
    iEnd = max(max(dElement["end"], dElement["separator"] or 0, dElement["comment"] or 0) for dElement in lGroup)
    lSlots = []
    for dElement in lGroup:
        lSlots.append(
            {
                "start": dElement["start"] - iStart,
                "end": dElement["end"] - iStart,
                "separator": None if dElement["separator"] is None else dElement["separator"] - iStart,
                "comment": None if dElement["comment"] is None else dElement["comment"] - iStart,
            },
        )
    lSources = [lGroup.index(dElement) for dElement in lExpected]
    iFirstMoved = next(i for i, dElement in enumerate(lGroup) if dElement is not lExpected[i])
    oReturn = oToi.extract_tokens(iStart, iEnd)
    # extract_tokens shares the meta data of oToi, and each group needs its own
    oReturn.dMetaData = {}
    oReturn.set_meta_data("line", lGroup[iFirstMoved]["line"])
    oReturn.set_meta_data(
        "action",
        {
            "order": [dElement["names"][0] for dElement in lExpected],
            "reason": sReason,
            "slots": lSlots,
            "sources": lSources,
        },
    )
    return oReturn


def reorder(lTokens, lSlots, lSources):
    """
    Puts the declaration and end of line comment of port lSources[i] in slot i.
    The semicolons, line breaks and indents stay where they are.
    """
    dSlotAtStart = {dSlot["start"]: iSlot for iSlot, dSlot in enumerate(lSlots)}
    setSkip = set()
    dInsertAfter = {}
    for iSlot, dSlot in enumerate(lSlots):
        iAnchor = dSlot["end"] if dSlot["separator"] is None else dSlot["separator"]
        if dSlot["comment"] is not None:
            # The original comment of the slot and the whitespace before it are replaced
            setSkip.update(range(iAnchor + 1, dSlot["comment"] + 1))
        dSource = lSlots[lSources[iSlot]]
        if dSource["comment"] is not None:
            dInsertAfter[iAnchor] = lTokens[dSource["comment"]]
    lReturn = []
    iIndex = 0
    while iIndex < len(lTokens):
        if iIndex in dSlotAtStart:
            iSlot = dSlotAtStart[iIndex]
            dSource = lSlots[lSources[iSlot]]
            lReturn.extend(lTokens[dSource["start"] : dSource["end"] + 1])
            iIndex = lSlots[iSlot]["end"]
        elif iIndex not in setSkip:
            lReturn.append(lTokens[iIndex])
        if iIndex in dInsertAfter:
            lReturn.append(parser.whitespace(" "))
            lReturn.append(dInsertAfter[iIndex])
        iIndex += 1
    return lReturn
