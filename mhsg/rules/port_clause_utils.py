# -*- coding: utf-8 -*-
"""
Splits a port clause into its port declarations and sections.

A section is a group of port declarations which is not interrupted by a blank
line or a comment line.  The comment lines directly above a section are its
header.
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


def get_elements(oToi):
    """
    Returns the port declarations of a port clause.

    Each declaration is a dictionary with:
      names : the identifiers
      mode : the mode, "in" if it is omitted
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
        if isinstance(oToken, token.interface_list.semicolon):
            dCurrent["separator"] = iToken
            lReturn.append(dCurrent)
            dPrevious = dCurrent
            dCurrent = None
            continue
        dCurrent["end"] = iToken
        if isinstance(oToken, lNameTokens):
            dCurrent["names"].append(oToken.get_value())
        elif type(oToken) in dModes:
            dCurrent["mode"] = dModes[type(oToken)]
    if dCurrent is not None:
        lReturn.append(dCurrent)
        # A comment after the close parenthesis is not part of the port clause
        if not any(isinstance(oToken, parser.carriage_return) for oToken in lTokens[dCurrent["end"] : -1]):
            dCurrent["close_on_same_line"] = True
    return [dElement for dElement in lReturn if len(dElement["names"]) > 0]


def new_element(iToken, iLine, iSection, lHeader):
    return {
        "names": [],
        "mode": "in",
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
