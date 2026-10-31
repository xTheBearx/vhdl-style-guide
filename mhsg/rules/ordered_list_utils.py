# -*- coding: utf-8 -*-
"""
Splits lists, such as the port declarations of a port clause or the
associations of a port map, into their elements and sections, and reorders
them.

A section is a group of elements which is not interrupted by a blank line or
a comment line.  The comment lines directly above a section are its header.
"""

from mhsg import parser, token

lNameTokens = (
    token.interface_unknown_declaration.identifier,
    token.interface_signal_declaration.identifier,
)

dModes = {
    token.mode.in_keyword: "in",
    token.mode.out_keyword: "out",
    token.mode.inout_keyword: "inout",
    token.mode.buffer_keyword: "buffer",
    token.mode.linkage_keyword: "linkage",
}


def get_port_clauses(oFile):
    """Returns the tokens from the open to the close parenthesis of each port clause."""
    return oFile.get_tokens_bounded_by(token.port_clause.open_parenthesis, token.port_clause.close_parenthesis)


def get_generic_clauses(oFile):
    """Returns the tokens from the open to the close parenthesis of each generic clause."""
    return oFile.get_tokens_bounded_by(token.generic_clause.open_parenthesis, token.generic_clause.close_parenthesis)


def get_interface_elements(oToi):
    """Returns the declarations of a generic or port clause, see split_list, with the words of each in names."""
    return split_list(oToi, token.interface_list.semicolon, update_words)


def update_words(dElement, oToken):
    dElement["names"].append(oToken.get_value())


def get_section_of_index(lElements, iIndex):
    """Returns the section of the element whose tokens include the token at iIndex."""
    for dElement in lElements:
        if dElement["start"] <= iIndex <= dElement["end"]:
            return dElement["section"]
    return 0


def get_elements(oToi):
    """Returns the port declarations of a port clause, see split_list."""
    return [dElement for dElement in split_list(oToi, token.interface_list.semicolon, update_port) if len(dElement["names"]) > 0]


def update_port(dElement, oToken):
    if isinstance(oToken, lNameTokens):
        dElement["names"].append(oToken.get_value())
    elif type(oToken) in dModes:
        dElement["mode"] = dModes[type(oToken)]


def get_associations(oToi):
    """
    Returns the associations of a port map, see split_list.
    For a named association, names holds the words of its formal part.
    """
    return split_list(oToi, token.association_list.comma, update_association)


def update_association(dElement, oToken):
    if isinstance(oToken, token.association_element.assignment):
        dElement["named"] = True
    elif not dElement["named"] and isinstance(oToken, (token.association_element.formal_part, parser.todo)):
        dElement["names"].append(oToken.get_value())


def split_list(oToi, oSeparator, fUpdate):
    """
    Returns the elements of the list between the first and last token of oToi.
    fUpdate(dElement, oToken) records what a rule needs from each token of an element.

    Each element is a dictionary with:
      names : filled by fUpdate
      mode : for a port, its mode, "in" if it is omitted
      named : for an association, True if it has a formal part
      start, end : indexes of its first and last token
      separator : index of the semicolon after it, or None for the last one
      comment : index of the comment at the end of its line, or None
      line : line number of its first token
      single_line : True if it does not span lines or contain comments
      section : number of its section
      header : the values of the comment lines directly above it
    """
    lTokens = oToi.get_tokens()
    iLine = oToi.get_line_number()
    lReturn = []
    dCurrent = None
    dPrevious = None
    bLineStart = False
    bBreak = False
    lHeader = []
    iSection = 0
    for iToken in range(1, len(lTokens) - 1):
        oToken = lTokens[iToken]
        if isinstance(oToken, parser.carriage_return):
            iLine += 1
            bLineStart = True
            if dCurrent is not None:
                dCurrent["line_break"] = True
            continue
        if isinstance(oToken, parser.whitespace):
            continue
        if isinstance(oToken, parser.blank_line):
            bBreak = True
            lHeader = []
            continue
        if isinstance(oToken, parser.comment):
            if bLineStart:
                if dCurrent is not None:
                    dCurrent["line_break"] = True
                else:
                    bBreak = True
                    lHeader.append(oToken.get_value())
            elif dCurrent is not None:
                dCurrent["comment"] = iToken
            elif dPrevious is not None:
                dPrevious["comment"] = iToken
            bLineStart = False
            continue
        bLineStart = False
        if dCurrent is None:
            if bBreak and len(lReturn) > 0:
                iSection += 1
            dCurrent = new_element(iToken, iLine, iSection, lHeader)
            bBreak = False
            lHeader = []
        elif dCurrent["line_break"]:
            # The declaration continues after a line break or a comment line
            dCurrent["single_line"] = False
        if isinstance(oToken, oSeparator):
            dCurrent["separator"] = iToken
            lReturn.append(dCurrent)
            dPrevious = dCurrent
            dCurrent = None
            continue
        dCurrent["end"] = iToken
        fUpdate(dCurrent, oToken)
    if dCurrent is not None:
        lReturn.append(dCurrent)
        # A comment after the close parenthesis is not part of the port clause
        if not any(isinstance(oToken, parser.carriage_return) for oToken in lTokens[dCurrent["end"] : -1]):
            dCurrent["close_on_same_line"] = True
    return lReturn


def new_element(iToken, iLine, iSection, lHeader):
    return {
        "names": [],
        "mode": "in",
        "named": False,
        "start": iToken,
        "end": iToken,
        "separator": None,
        "comment": None,
        "line": iLine,
        "single_line": True,
        "section": iSection,
        "header": lHeader,
        "close_on_same_line": False,
        "line_break": False,
    }


def get_sections(lElements):
    """Returns the elements grouped by section."""
    dSections = {}
    for dElement in lElements:
        dSections.setdefault(dElement["section"], []).append(dElement)
    return [dSections[iSection] for iSection in sorted(dSections)]


def get_context(oFile, oToi):
    """
    Returns ("entity", name), ("component", name) or ("other", None) for the
    design unit a port clause belongs to.
    """
    lTokens = oFile.lAllObjects
    for iIndex in range(oToi.get_start_index() - 1, -1, -1):
        oToken = lTokens[iIndex]
        if isinstance(oToken, token.entity_declaration.identifier):
            return "entity", oToken.get_value()
        if isinstance(oToken, token.component_declaration.identifier):
            return "component", oToken.get_value()
        if isinstance(oToken, (token.block_statement.block_keyword, token.architecture_body.begin_keyword)):
            return "other", None
    return "other", None


def create_group_toi(oToi, lGroup, lExpected, sReason):
    """
    Returns the tokens of a group of elements.  Each element's position in the group is a slot:
    the element in the first slot is replaced by the first element of the expected order, and so on.
    sReason is why the group is not reordered, or None.
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
    Puts the element and end of line comment of element lSources[i] in slot i.
    The separators, line breaks and indents stay where they are.
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
