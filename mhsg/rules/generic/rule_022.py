# -*- coding: utf-8 -*-

from mhsg import parser, token, violation
from mhsg.rule_group import structure
from mhsg.rules import ordered_list_utils
from mhsg.vhdlFile import utils

lNameTokens = (
    token.interface_constant_declaration.identifier,
    token.interface_file_declaration.identifier,
    token.interface_incomplete_type_declaration.identifier,
    token.interface_signal_declaration.identifier,
    token.interface_unknown_declaration.identifier,
    token.interface_variable_declaration.identifier,
    token.interface_function_specification.designator,
    token.interface_procedure_specification.designator,
)

lIgnoreTokens = (parser.whitespace, parser.carriage_return, parser.blank_line, parser.comment)


class rule_022(structure.Rule):
    """
    This rule checks generics are declared in alphabetical order.

    A generic may use generics declared before it, for example in its default value.
    Such a generic is expected after the generics it uses, so the expected order is alphabetical wherever the dependencies allow.
    Names are compared ignoring case.

    With the :code:`sort_within_sections` option set to :code:`yes` (default), each group of generics separated by a blank line or comment line is sorted on its own.
    :code:`no` sorts the whole generic list.

    .. NOTE:: This rule is disabled by default.

    By default the rule only reports the expected order.
    Moving the generics of an entity changes what a direct instantiation with positional generic association connects to.
    With :code:`move_generics` set to :code:`when_safe`, the generics of an entity are moved if no file of the run instantiates it directly with a positional generic association.
    Instances in files that are not part of the run are not checked, and input from stdin is never moved.
    Generics of components, packages and subprograms are only reported.
    Generics are only moved if each declaration is on a line of its own; comments at the end of a line move with their generic.

    **Violation**

    .. code-block:: vhdl

       generic (
         G_WIDTH : integer := 8;
         G_DEPTH : integer := 16;
         G_ADDR_WIDTH : integer := G_DEPTH / 4
       );

    **Fix**

    .. code-block:: vhdl

       generic (
         G_DEPTH : integer := 16;
         G_ADDR_WIDTH : integer := G_DEPTH / 4;
         G_WIDTH : integer := 8
       );
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.configuration_documentation_link = None
        self.move_generics = "never"
        self.configuration.append("move_generics")
        self.sort_within_sections = "yes"
        self.configuration.append("sort_within_sections")

    def _get_tokens_of_interest(self, oFile):
        bWithinSections = utils.convert_yes_no_option_to_boolean(self.sort_within_sections)
        lPositional = getattr(oFile.configuration, "project_positional_generic_entities", None)
        lReturn = []
        for oToi in ordered_list_utils.get_generic_clauses(oFile):
            lElements = get_elements(oToi)
            lSplit = ordered_list_utils.get_interface_elements(oToi)
            # The declaration of each generic, with its separator, comment and section
            dSplit = {id(dElement): find_split_element(lSplit, dElement["index"]) for dElement in lElements}
            if bWithinSections:
                dGroups = {}
                for dElement in lElements:
                    dGroups.setdefault(dSplit[id(dElement)]["section"], []).append(dElement)
                lGroups = [dGroups[iSection] for iSection in sorted(dGroups)]
            else:
                lGroups = [lElements]
            sKind, sName = ordered_list_utils.get_generic_context(oFile, oToi)
            for lGroup in lGroups:
                lExpected = get_expected_order(lGroup)
                if lExpected == lGroup:
                    continue
                lSplitGroup = [dSplit[id(dElement)] for dElement in lGroup]
                lSplitExpected = [dSplit[id(dElement)] for dElement in lExpected]
                sReason = self._reason_not_moved(sKind, sName, lPositional, lSplitGroup, lSplit, bWithinSections)
                oGroup = ordered_list_utils.create_group_toi(oToi, lSplitGroup, lSplitExpected, sReason)
                oGroup.get_meta_data("action")["order"] = [dElement["names"][0] for dElement in lExpected]
                lReturn.append(oGroup)
        return lReturn

    def _reason_not_moved(self, sKind, sName, lPositional, lGroup, lElements, bWithinSections):
        if self.move_generics != "when_safe":
            return "move_generics is never"
        if sKind == "component":
            return "generics of component declarations are not moved"
        if sKind != "entity":
            return "only generics of entities are moved"
        if lPositional is None:
            return "the instances of the entity are not known"
        if sName.lower() in lPositional:
            return "the entity is instantiated with positional generic association"
        if not bWithinSections and len(ordered_list_utils.get_sections(lElements)) > 1:
            return "the generics are separated by blank lines or comments"
        for dElement in lGroup:
            if not dElement["single_line"] or dElement["close_on_same_line"]:
                return "a generic declaration is not on a line of its own"
        return None

    def _analyze(self, lToi):
        for oToi in lToi:
            dAction = oToi.get_meta_data("action")
            sSolution = "Order generics alphabetically: " + ", ".join(dAction["order"])
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


def find_split_element(lSplit, iIndex):
    for dElement in lSplit:
        if dElement["start"] <= iIndex <= dElement["end"]:
            return dElement
    return None


def get_elements(oToi):
    """
    Splits a generic clause into its interface elements.
    Each element has its names, the lower case values of the other words in it, and the line and token index of its first name.
    """
    lReturn = []
    lTokens = oToi.get_tokens()
    iLine = oToi.get_line_number()
    iDepth = 0
    dElement = new_element()
    bPackageName = False
    # Skip the opening and closing parentheses of the generic clause
    for iToken, oToken in enumerate(lTokens[:-1]):
        if iToken == 0:
            continue
        if isinstance(oToken, parser.carriage_return):
            iLine += 1
            continue
        if isinstance(oToken, lIgnoreTokens):
            continue
        if isinstance(oToken, parser.open_parenthesis):
            iDepth += 1
        elif isinstance(oToken, parser.close_parenthesis):
            iDepth -= 1
        if iDepth == 0 and isinstance(oToken, token.interface_list.semicolon):
            add_element(dElement, lReturn)
            dElement = new_element()
            continue
        if isinstance(oToken, lNameTokens) or bPackageName:
            add_name(dElement, oToken, iLine, iToken)
            bPackageName = False
        else:
            dElement["words"].add(oToken.get_value().lower())
            bPackageName = isinstance(oToken, token.interface_package_declaration.package_keyword)
    add_element(dElement, lReturn)
    return lReturn


def new_element():
    return {"names": [], "words": set(), "line": None, "index": None}


def add_name(dElement, oToken, iLine, iToken):
    if dElement["line"] is None:
        dElement["line"] = iLine
        dElement["index"] = iToken
    dElement["names"].append(oToken.get_value())


def add_element(dElement, lElements):
    if len(dElement["names"]) > 0:
        lElements.append(dElement)


def get_expected_order(lElements):
    """
    Orders the elements alphabetically, keeping each element after the elements whose names it uses.
    """
    lReturn = []
    lRemaining = list(lElements)
    while len(lRemaining) > 0:
        lAvailable = [dElement for dElement in lRemaining if not depends_on_any(dElement, lRemaining)]
        if len(lAvailable) == 0:
            # Circular references are not valid VHDL; keep the remaining elements as they are
            lReturn.extend(lRemaining)
            break
        dNext = min(lAvailable, key=lambda dElement: dElement["names"][0].lower())
        lReturn.append(dNext)
        lRemaining.remove(dNext)
    return lReturn


def depends_on_any(dElement, lElements):
    for dOther in lElements:
        if dOther is dElement:
            continue
        for sName in dOther["names"]:
            if sName.lower() in dElement["words"]:
                return True
    return False
