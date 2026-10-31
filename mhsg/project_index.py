# -*- coding: utf-8 -*-
"""
Names declared in the files of a run, so a rule checking one file can recognize names declared in another.
"""

import re

# Types and subtypes declared in the standard and IEEE packages
STANDARD_TYPE_NAMES = {
    # std.standard
    "bit",
    "bit_vector",
    "boolean",
    "boolean_vector",
    "character",
    "delay_length",
    "file_open_kind",
    "file_open_status",
    "integer",
    "integer_vector",
    "natural",
    "positive",
    "real",
    "real_vector",
    "severity_level",
    "string",
    "time",
    "time_vector",
    # std.textio
    "line",
    "side",
    "text",
    "width",
    # ieee.std_logic_1164
    "std_logic",
    "std_logic_vector",
    "std_ulogic",
    "std_ulogic_vector",
    # ieee.numeric_std and ieee.numeric_bit
    "signed",
    "unsigned",
    "u_signed",
    "u_unsigned",
    "unresolved_signed",
    "unresolved_unsigned",
    # ieee.fixed_pkg and ieee.float_pkg
    "float",
    "float128",
    "float32",
    "float64",
    "sfixed",
    "ufixed",
    "u_sfixed",
    "u_ufixed",
    "unresolved_float",
    "unresolved_sfixed",
    "unresolved_ufixed",
}

reComment = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)
reString = re.compile(r'"[^"\n]*"')
reTypeDeclaration = re.compile(r"\b(?:sub)?type\s+([a-z][a-z0-9_]*)\s+is\b", re.IGNORECASE)


def collect_type_names(lFilenames):
    """
    Returns the lower case names of the types and subtypes declared in the files.
    Files which cannot be read are skipped, since they are reported when they are checked.
    """
    lReturn = set()
    for sFilename in lFilenames or []:
        try:
            with open(sFilename, encoding="utf-8", errors="replace") as oFile:
                sText = oFile.read()
        except OSError:
            continue
        lReturn.update(get_type_names(sText))
    return lReturn


def get_type_names(sText):
    sText = reComment.sub(" ", sText)
    sText = reString.sub(" ", sText)
    return {sName.lower() for sName in reTypeDeclaration.findall(sText)}


reEntityInstantiation = re.compile(r"\bentity\s+[a-z][a-z0-9_]*\s*\.\s*([a-z][a-z0-9_]*)", re.IGNORECASE)
rePortMap = re.compile(r"\bport\s+map\s*\(", re.IGNORECASE)


def read_files(lFilenames):
    for sFilename in lFilenames or []:
        try:
            with open(sFilename, encoding="utf-8", errors="replace") as oFile:
                yield oFile.read()
        except OSError:
            continue


def collect_positional_entity_instantiations(lFilenames):
    """
    Returns the lower case names of the entities which are instantiated directly
    (entity lib.name) with at least one positional port association in the files.
    Reordering the ports of such an entity would change what these instances connect.
    """
    lReturn = set()
    for sText in read_files(lFilenames):
        lReturn.update(get_positional_entity_instantiations(sText))
    return lReturn


def get_positional_entity_instantiations(sText):
    sText = reComment.sub(" ", sText)
    sText = reString.sub('""', sText)
    lReturn = set()
    for oMatch in reEntityInstantiation.finditer(sText):
        sStatement = get_statement(sText, oMatch.end())
        oPortMap = rePortMap.search(sStatement)
        if oPortMap is None:
            continue
        sAssociations = get_parenthesized(sStatement, oPortMap.end())
        if any("=>" not in sElement for sElement in split_top_level(sAssociations)):
            lReturn.add(oMatch.group(1).lower())
    return lReturn


def get_statement(sText, iStart):
    """Returns the text from iStart to the next semicolon outside of parentheses."""
    iDepth = 0
    for iIndex in range(iStart, len(sText)):
        sChar = sText[iIndex]
        if sChar == "(":
            iDepth += 1
        elif sChar == ")":
            iDepth -= 1
        elif sChar == ";" and iDepth <= 0:
            return sText[iStart:iIndex]
    return sText[iStart:]


def get_parenthesized(sText, iStart):
    """Returns the text after an open parenthesis up to its matching close parenthesis."""
    iDepth = 1
    for iIndex in range(iStart, len(sText)):
        if sText[iIndex] == "(":
            iDepth += 1
        elif sText[iIndex] == ")":
            iDepth -= 1
            if iDepth == 0:
                return sText[iStart:iIndex]
    return sText[iStart:]


def split_top_level(sText):
    """Splits a list of associations at the commas outside of parentheses."""
    lReturn = []
    iDepth = 0
    iStart = 0
    for iIndex, sChar in enumerate(sText):
        if sChar == "(":
            iDepth += 1
        elif sChar == ")":
            iDepth -= 1
        elif sChar == "," and iDepth == 0:
            lReturn.append(sText[iStart:iIndex])
            iStart = iIndex + 1
    lReturn.append(sText[iStart:])
    return [sElement for sElement in lReturn if sElement.strip()]


reEntityOrComponent = re.compile(r"\b(entity|component)\s+([a-z][a-z0-9_]*)\s+is\b|\bcomponent\s+([a-z][a-z0-9_]*)\b(?!\s*port\s+map)", re.IGNORECASE)
rePort = re.compile(r"\bport\s*\(", re.IGNORECASE)
reEnd = re.compile(r"\bend\b", re.IGNORECASE)


def collect_port_orders(lFilenames):
    """
    Returns {"entity": {name: ports}, "component": {name: ports}} with the lower case port
    names of each entity and component declaration in the files, in declaration order.
    A name declared more than once with different ports maps to None, since it is not
    known which declaration an instance uses.
    """
    dReturn = {"entity": {}, "component": {}}
    for sText in read_files(lFilenames):
        for sKind, sName, lPorts in get_port_orders(sText):
            dKind = dReturn[sKind]
            if sName in dKind and dKind[sName] != lPorts:
                dKind[sName] = None
            else:
                dKind[sName] = lPorts
    return dReturn


def get_port_orders(sText):
    """Returns (kind, name, ports) for each entity and component declaration in the text."""
    sText = reComment.sub(" ", sText)
    sText = reString.sub('""', sText)
    lReturn = []
    for oMatch in reEntityOrComponent.finditer(sText):
        if oMatch.group(1) is not None:
            sKind, sName = oMatch.group(1).lower(), oMatch.group(2).lower()
        else:
            # "component name" without "is"; an instance "u : component name port map" is skipped above
            sKind, sName = "component", oMatch.group(3).lower()
        oEnd = reEnd.search(sText, oMatch.end())
        iEnd = oEnd.start() if oEnd is not None else len(sText)
        oPort = rePort.search(sText, oMatch.end(), iEnd)
        if oPort is None:
            continue
        lPorts = []
        for sDeclaration in get_parenthesized(sText, oPort.end()).split(";"):
            if ":" in sDeclaration:
                sNames = re.sub(r"^\s*signal\b", "", sDeclaration.split(":")[0], flags=re.IGNORECASE)
                lPorts.extend(sName.strip().lower() for sName in sNames.split(",") if sName.strip())
        lReturn.append((sKind, sName, tuple(lPorts)))
    return lReturn
