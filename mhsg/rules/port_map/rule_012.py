# -*- coding: utf-8 -*-

from mhsg import token, violation
from mhsg.rule_group import structure
from mhsg.rules import ordered_list_utils
from mhsg.vhdlFile import utils

lStopTokens = (
    token.component_instantiation_statement.semicolon,
    token.architecture_body.begin_keyword,
    token.block_statement.block_keyword,
)


class rule_012(structure.Rule):
    """
    This rule checks the order of the associations in port maps.

    .. NOTE:: This rule is disabled by default.

    The order is set by these options:

    * :code:`order`: :code:`declaration` (default) follows the order of the ports in the entity or component declaration.
      :code:`name` sorts the associations by the name of their formal part.
    * :code:`sort_within_sections`: :code:`yes` (default) sorts each group of associations separated by a blank line or comment line on its own.
      :code:`no` sorts the whole port map.

    The declaration is looked up in the file and in the other files of the run.
    A component instance uses the component declaration, or the entity of the same name if there is none.
    Port maps are not checked if the declaration is not known, if it is declared differently in several places, if a formal part is not one of its ports, or if they use positional association.
    Associations of the same port, such as :code:`data(0)` and :code:`data(1)`, keep their order.

    Moving named associations does not change what the instance connects, so the rule moves them if each association is on a line of its own.
    Comments at the end of a line move with their association.
    When port_028 moves the ports of an entity in another file, run the fix again so the port maps follow the new order.

    **Violation**

    .. code-block:: vhdl

       entity sub is
         port (
           clk  : in  std_logic;
           data : out std_logic
         );
       end entity sub;

       u_sub : entity work.sub
         port map (
           data => s_data,
           clk  => clk
         );

    **Fix**

    .. code-block:: vhdl

       u_sub : entity work.sub
         port map (
           clk  => clk,
           data => s_data
         );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Order associations"
        self.phase = 1
        # After port_028, which can reorder the declarations in the same file
        self.subphase = 6
        self.disable = True
        self.order = "declaration"
        self.configuration.append("order")
        self.sort_within_sections = "yes"
        self.configuration.append("sort_within_sections")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        bWithinSections = utils.convert_yes_no_option_to_boolean(self.sort_within_sections)
        dLocal = get_local_declarations(oFile)
        dProject = getattr(oFile.configuration, "project_port_orders", None) or {"entity": {}, "component": {}}
        lReturn = []
        for oToi in oFile.get_tokens_bounded_by(token.port_map_aspect.open_parenthesis, token.port_map_aspect.close_parenthesis):
            lElements = ordered_list_utils.get_associations(oToi)
            if len(lElements) == 0 or not all(dElement["named"] for dElement in lElements):
                continue
            sKind, sName = get_instantiated_unit(oFile, oToi)
            if sKind is None:
                continue
            if self.order == "name":
                fKey = name_key
                sMessage = "Order associations by name"
            else:
                lPorts = find_ports(sKind, sName, dLocal, dProject)
                if lPorts is None:
                    continue
                fKey = declaration_key(lPorts)
                if any(fKey(dElement) is None for dElement in lElements):
                    continue
                sMessage = "Order associations as in the declaration of " + sName
            if bWithinSections:
                lGroups = ordered_list_utils.get_sections(lElements)
            else:
                lGroups = [lElements]
            for lGroup in lGroups:
                lExpected = sorted(lGroup, key=fKey)
                if lExpected == lGroup:
                    continue
                sReason = reason_not_moved(lGroup, lElements, bWithinSections)
                oGroup = ordered_list_utils.create_group_toi(oToi, lGroup, lExpected, sReason)
                oGroup.get_meta_data("action")["order"] = [formal_label(dElement, fKey) for dElement in lExpected]
                oGroup.set_meta_data("message", sMessage)
                lReturn.append(oGroup)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            dAction = oToi.get_meta_data("action")
            sSolution = oToi.get_meta_data("message") + ": " + ", ".join(dAction["order"])
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


def get_local_declarations(oFile):
    """Returns {(kind, name): ports} for the entity and component declarations in the file."""
    dReturn = {}
    for oToi in ordered_list_utils.get_port_clauses(oFile):
        sKind, sName = ordered_list_utils.get_context(oFile, oToi)
        if sName is None:
            continue
        lPorts = [sPort.lower() for dElement in ordered_list_utils.get_elements(oToi) for sPort in dElement["names"]]
        dReturn[(sKind, sName.lower())] = lPorts
    return dReturn


def get_instantiated_unit(oFile, oToi):
    """Returns ("entity", name) or ("component", name) for the instance a port map belongs to."""
    lTokens = oFile.lAllObjects
    for iIndex in range(oToi.get_start_index() - 1, -1, -1):
        oToken = lTokens[iIndex]
        if isinstance(oToken, token.instantiated_unit.entity_name):
            return "entity", oToken.get_value()
        if isinstance(oToken, token.instantiated_unit.component_name):
            return "component", oToken.get_value()
        if isinstance(oToken, lStopTokens):
            break
    return None, None


def find_ports(sKind, sName, dLocal, dProject):
    sName = sName.lower()
    lKinds = ["entity"] if sKind == "entity" else ["component", "entity"]
    for sLookup in lKinds:
        if (sLookup, sName) in dLocal:
            return dLocal[(sLookup, sName)]
        if sName in dProject[sLookup]:
            # None if the name is declared more than once with different ports
            return dProject[sLookup][sName]
    return None


def declaration_key(lPorts):
    def key(dElement):
        # The first word of the formal part that is a port, so a conversion function is skipped
        for sWord in dElement["names"]:
            if sWord.lower() in lPorts:
                return lPorts.index(sWord.lower())
        return None

    return key


def name_key(dElement):
    return dElement["names"][0].lower()


def formal_label(dElement, fKey):
    if fKey is name_key:
        return dElement["names"][0]
    for sWord in dElement["names"]:
        if fKey({"names": [sWord]}) is not None:
            return sWord
    return dElement["names"][0]


def reason_not_moved(lGroup, lElements, bWithinSections):
    if not bWithinSections and len(ordered_list_utils.get_sections(lElements)) > 1:
        return "the associations are separated by blank lines or comments"
    # In a port map on a single line, a comment after the close parenthesis belongs to the whole instance
    bOneLine = all(dElement["single_line"] and dElement["line"] == lElements[0]["line"] for dElement in lElements)
    if bOneLine:
        return None
    for dElement in lGroup:
        if not dElement["single_line"] or dElement["close_on_same_line"]:
            return "an association is not on a line of its own"
    return None
