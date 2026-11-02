# -*- coding: utf-8 -*-

import fnmatch

from mhsg import violation
from mhsg.rule_group import structure
from mhsg.rules import ordered_list_utils
from mhsg.vhdlFile import utils

lKeys = ["clock_reset", "direction", "name"]


CLOCK_WORDS = ["clk", "clock", "*clk", "clk[0-9]*", "*clk[0-9]*", "clock[0-9]*", "clkin", "clkout", "clockin", "clockout"]
# Listed instead of *rst and *reset, which would also match words such as first, burst and preset
RESET_WORDS = [
    "rst",
    "rstn",
    "rstb",
    "rst[0-9]*",
    "nrst",
    "arst",
    "arstn",
    "srst",
    "srstn",
    "reset",
    "resetn",
    "nreset",
    "areset",
    "aresetn",
    "sreset",
    "sresetn",
    "presetn",
]
QUALIFIER_WORDS = ["en", "ena", "enable", "sel", "div", "cnt", "count", "gate", "locked", "stable", "valid", "req", "ack", "done"]


class rule_028(structure.Rule):
    """
    This rule checks the order of port declarations.

    .. NOTE:: This rule is disabled by default.

    The order is set by these options:

    * :code:`order`: the sort keys, most important first.
      The keys are :code:`clock_reset`, :code:`direction` and :code:`name`.
      The default is :code:`[clock_reset, direction, name]`.
    * :code:`clock_words`, :code:`reset_words` and :code:`qualifier_words`: words of port names for the :code:`clock_reset` key.
      A name is split into words at its underscores, so :code:`s_axi_aclk` has the words :code:`s`, :code:`axi` and :code:`aclk`.
      A port is a clock if one of its words matches :code:`clock_words`, and a reset if one matches :code:`reset_words`, unless one of its words matches :code:`qualifier_words`.
      The words can use :code:`*` and :code:`[0-9]` as in file name patterns.
      Clocks come first, then resets, then the other ports.
      With the defaults, :code:`clk_i`, :code:`sys_clk`, :code:`s_axi_aclk` and :code:`clk_100mhz` are clocks, and :code:`rst_n` and :code:`s_axi_aresetn` are resets,
      but :code:`clk_en`, :code:`clk_sel`, :code:`rst_done` and :code:`reset_req` are neither.
    * :code:`differential_suffixes`: pairs of suffixes of differential ports, default :code:`[[_p, _n]]`.
      When both ports of a pair, such as :code:`sys_clk_p` and :code:`sys_clk_n`, are in the port list, the :code:`name` key sorts them by their shared name with the positive port first.
      A port without its other half, such as the active low reset :code:`rst_n`, is sorted by its own name.
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
    Instances in files that are not part of the run are not checked, unless the files are listed in index_file_list or given with --index_files.
    Input from stdin is never moved.
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
        self.clock_words = list(CLOCK_WORDS)
        self.configuration.append("clock_words")
        self.reset_words = list(RESET_WORDS)
        self.configuration.append("reset_words")
        self.qualifier_words = list(QUALIFIER_WORDS)
        self.configuration.append("qualifier_words")
        self.differential_suffixes = [["_p", "_n"]]
        self.configuration.append("differential_suffixes")
        self._dPairs = {}
        self.sort_within_sections = "yes"
        self.configuration.append("sort_within_sections")
        self.move_ports = "never"
        self.configuration.append("move_ports")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        bWithinSections = utils.convert_yes_no_option_to_boolean(self.sort_within_sections)
        lPositional = getattr(oFile.configuration, "project_positional_entities", None)
        lReturn = []
        for oToi in ordered_list_utils.get_port_clauses(oFile):
            lElements = ordered_list_utils.get_elements(oToi)
            self._dPairs = get_differential_pairs(lElements, self.differential_suffixes)
            sKind, sName = ordered_list_utils.get_context(oFile, oToi)
            if bWithinSections:
                lGroups = ordered_list_utils.get_sections(lElements)
            else:
                lGroups = [lElements]
            for lGroup in lGroups:
                lExpected = sorted(lGroup, key=self._sort_key)
                if lExpected == lGroup:
                    continue
                sReason = self._reason_not_moved(sKind, sName, lPositional, lGroup, lElements, bWithinSections)
                lReturn.append(ordered_list_utils.create_group_toi(oToi, lGroup, lExpected, sReason))
        return lReturn

    def _sort_key(self, dElement):
        lReturn = []
        for sKey in self.order:
            if sKey == "clock_reset":
                lReturn.append(self._clock_reset_rank(dElement["names"][0]))
            elif sKey == "direction":
                lReturn.append(direction_rank(dElement["mode"], self.direction_order))
            elif sKey == "name":
                sName = dElement["names"][0].lower()
                lReturn.append(self._dPairs.get(sName, (sName, 0)))
        return lReturn

    def _clock_reset_rank(self, sName):
        return clock_reset_rank(sName, self.clock_words, self.reset_words, self.qualifier_words)

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
        if not bWithinSections and len(ordered_list_utils.get_sections(lElements)) > 1:
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
        oViolation.set_tokens(ordered_list_utils.reorder(oViolation.get_tokens(), dAction["slots"], dAction["sources"]))


def direction_rank(sMode, lDirectionOrder):
    lOrder = [sDirection.lower() for sDirection in lDirectionOrder]
    if sMode in lOrder:
        return lOrder.index(sMode)
    return len(lOrder)


def get_differential_pairs(lElements, lSuffixes):
    """
    Returns {name: (shared name, 0 or 1)} for the ports which form a differential pair, such as
    clk_p and clk_n, so the positive port sorts directly before the negative one.
    A port is only part of a pair if the other port of the pair is in the same port list,
    so an active low reset such as rst_n is not.
    """
    setNames = {dElement["names"][0].lower() for dElement in lElements}
    dReturn = {}
    for lPair in lSuffixes:
        sPositive, sNegative = (sSuffix.lower() for sSuffix in lPair)
        for sName in setNames:
            if not sName.endswith(sPositive) or len(sName) == len(sPositive):
                continue
            sBase = sName[: -len(sPositive)]
            if sBase + sNegative in setNames:
                dReturn[sName] = (sBase, 0)
                dReturn[sBase + sNegative] = (sBase, 1)
    return dReturn


def clock_reset_rank(sName, lClockWords=CLOCK_WORDS, lResetWords=RESET_WORDS, lQualifierWords=QUALIFIER_WORDS):
    """
    Returns 0 for a clock name, 1 for a reset name and 2 for any other name.
    The name is split into words at underscores; a qualifier word such as en makes it neither.
    """
    lWords = [sWord for sWord in sName.lower().split("_") if sWord != ""]
    if any_word_matches(lWords, lQualifierWords):
        return 2
    if any_word_matches(lWords, lClockWords):
        return 0
    if any_word_matches(lWords, lResetWords):
        return 1
    return 2


def is_reset_name(sName):
    return clock_reset_rank(sName) == 1


def any_word_matches(lWords, lPatterns):
    return any(fnmatch.fnmatchcase(sWord, sPattern.lower()) for sWord in lWords for sPattern in lPatterns)
