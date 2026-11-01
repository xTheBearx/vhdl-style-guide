# -*- coding: utf-8 -*-

from mhsg import parser, token, violation
from mhsg.rule_group import case
from mhsg.vhdlFile.extract import tokens

lIgnoreTokens = (parser.comment, parser.character_literal, parser.string_literal, parser.whitespace, parser.carriage_return, parser.blank_line)


class rule_503(case.Rule):
    """
    This rule checks record element names are used with the same capitalization as in the record type declaration.

    Element names are checked in selected names, such as **rec.element**, whose prefix is declared in the file,
    and in the choices of aggregates, such as **(element => value)**.
    Element names declared with different capitalizations in different records, or which also name another declaration, are not checked.

    **Violation**

    .. code-block:: vhdl

       type t_rec is record
         sl_Valid : std_logic;
       end record t_rec;

       constant c_rec : t_rec := (sl_valid => '0');

       rec.SL_VALID <= '1';

    **Fix**

    .. code-block:: vhdl

       type t_rec is record
         sl_Valid : std_logic;
       end record t_rec;

       constant c_rec : t_rec := (sl_Valid => '0');

       rec.sl_Valid <= '1';
    """

    def __init__(self):
        super().__init__()
        self.subphase = 2
        self.groups.append("case::name")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lAllTokens = oFile.lAllObjects
        dElements, lOtherNames = get_declared_names(lAllTokens)
        lReturn = []
        oTokenMap = oFile.get_token_map()
        for iToken, oToken in enumerate(lAllTokens):
            if isinstance(oToken, lIgnoreTokens) or isinstance(oToken, token.identifier_list.identifier):
                continue
            sValue = oToken.get_value()
            if sValue is None:
                continue
            if "." in sValue:
                sExpected = fix_selected_name(sValue, dElements, lOtherNames)
            elif is_aggregate_choice(iToken, lAllTokens) and sValue.lower() in dElements and sValue.lower() not in lOtherNames:
                sExpected = dElements[sValue.lower()]
            else:
                continue
            if sExpected is not None and sExpected != sValue:
                oToi = tokens.New(iToken, oTokenMap.get_line_number_of_index(iToken), [oToken])
                oToi.set_meta_data("expected", sExpected)
                lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            sExpected = oToi.get_meta_data("expected")
            sActual = oToi.get_tokens()[0].get_value()
            oViolation = violation.New(oToi.get_line_number(), oToi, f"Change {sActual} to {sExpected}")
            oViolation.set_action({"expected": sExpected})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        lTokens[0].set_value(oViolation.get_action()["expected"])
        oViolation.set_tokens(lTokens)


def get_declared_names(lAllTokens):
    """
    Returns the record element names, mapped from lower case to their declared case, and the lower case names of all other declarations.
    Element names declared with different capitalizations are left out.
    """
    dElements = {}
    lConflicts = set()
    lOtherNames = set()
    bInRecord = False
    for oToken in lAllTokens:
        if isinstance(oToken, token.record_type_definition.record_keyword):
            bInRecord = True
        elif isinstance(oToken, token.record_type_definition.end_keyword):
            bInRecord = False
        elif bInRecord and isinstance(oToken, token.identifier_list.identifier):
            sLower = oToken.get_value().lower()
            if sLower in dElements and dElements[sLower] != oToken.get_value():
                lConflicts.add(sLower)
            dElements[sLower] = oToken.get_value()
        elif isinstance(oToken, (parser.identifier, parser.designator)):
            lOtherNames.add(oToken.get_value().lower())
    for sLower in lConflicts:
        del dElements[sLower]
    return dElements, lOtherNames


def fix_selected_name(sValue, dElements, lOtherNames):
    """
    Returns the selected name with the record elements in their declared case, or None if the prefix is not declared in the file.
    """
    lSegments = sValue.split(".")
    if lSegments[0].lower() not in lOtherNames:
        return None
    for iSegment in range(1, len(lSegments)):
        sLower = lSegments[iSegment].lower()
        if sLower in dElements and sLower not in lOtherNames:
            lSegments[iSegment] = dElements[sLower]
    return ".".join(lSegments)


def is_aggregate_choice(iToken, lAllTokens):
    for iIndex in range(iToken + 1, len(lAllTokens)):
        oToken = lAllTokens[iIndex]
        if isinstance(oToken, parser.whitespace):
            continue
        return isinstance(oToken, token.element_association.assignment)
    return False
