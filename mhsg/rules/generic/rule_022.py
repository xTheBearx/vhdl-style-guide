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
       It only reports the expected order, because moving generics by hand keeps their comments where they belong.

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
        self.fixable = False
        self.configuration_documentation_link = None
        self.sort_within_sections = "yes"
        self.configuration.append("sort_within_sections")

    def _get_tokens_of_interest(self, oFile):
        return oFile.get_tokens_bounded_by(token.generic_clause.open_parenthesis, token.generic_clause.close_parenthesis)

    def _analyze(self, lToi):
        bWithinSections = utils.convert_yes_no_option_to_boolean(self.sort_within_sections)
        for oToi in lToi:
            lElements = get_elements(oToi)
            if bWithinSections:
                lSections = ordered_list_utils.get_interface_elements(oToi)
                dGroups = {}
                for dElement in lElements:
                    dGroups.setdefault(ordered_list_utils.get_section_of_index(lSections, dElement["index"]), []).append(dElement)
                lGroups = [dGroups[iSection] for iSection in sorted(dGroups)]
            else:
                lGroups = [lElements]
            for lGroup in lGroups:
                self._check_order(oToi, lGroup)

    def _check_order(self, oToi, lElements):
        lExpected = get_expected_order(lElements)
        for dActual, dExpected in zip(lElements, lExpected):
            if dActual is not dExpected:
                sOrder = ", ".join(dElement["names"][0] for dElement in lExpected)
                sSolution = "Order generics alphabetically: " + sOrder
                oViolation = violation.New(dActual["line"], oToi.extract_tokens(dActual["index"], dActual["index"]), sSolution)
                self.add_violation(oViolation)
                break


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
