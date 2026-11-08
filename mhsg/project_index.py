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


reEnumeratedType = re.compile(r"\btype\s+([a-z][a-z0-9_]*)\s+is\s*\(([^()]*)\)\s*;", re.IGNORECASE)
reEnumerationLiteral = re.compile(r"^(?:[a-z][a-z0-9_]*|'.')$", re.IGNORECASE)


def collect_enumerated_types(lFilenames):
    """
    Returns {lower case type name: values as written, in order} for the enumerated types declared in the files, such
    as the state type of a package, for the rules on state machines whose type another file declares. A name declared
    with other values in two files is left out, as a rule cannot tell which one a file uses.
    """
    dReturn = {}
    setAmbiguous = set()
    for sText in read_files(lFilenames):
        for sName, lValues in get_enumerated_types(sText).items():
            if sName in dReturn and [s.lower() for s in dReturn[sName]] != [s.lower() for s in lValues]:
                setAmbiguous.add(sName)
            dReturn.setdefault(sName, lValues)
    return {s: l for s, l in dReturn.items() if s not in setAmbiguous}


def get_enumerated_types(sText):
    sText = reComment.sub(" ", sText)
    sText = reString.sub(" ", sText)
    dReturn = {}
    for sName, sValues in reEnumeratedType.findall(sText):
        lValues = [s.strip() for s in sValues.split(",")]
        if lValues and all(reEnumerationLiteral.match(s) for s in lValues):
            dReturn[sName.lower()] = lValues
    return dReturn


reEntityInstantiation = re.compile(r"\bentity\s+[a-z][a-z0-9_]*\s*\.\s*([a-z][a-z0-9_]*)", re.IGNORECASE)
rePortMap = re.compile(r"\bport\s+map\s*\(", re.IGNORECASE)
reGenericMap = re.compile(r"\bgeneric\s+map\s*\(", re.IGNORECASE)


def read_files(lFilenames):
    for sFilename in lFilenames or []:
        try:
            with open(sFilename, encoding="utf-8", errors="replace") as oFile:
                yield oFile.read()
        except OSError:
            continue


def collect_positional_entity_instantiations(lFilenames, sMap="port"):
    """
    Returns the lower case names of the entities which are instantiated directly
    (entity lib.name) with at least one positional association in their port map,
    or their generic map if sMap is "generic", in the files.
    Reordering the ports or generics of such an entity would change what these instances connect.
    """
    lReturn = set()
    for sText in read_files(lFilenames):
        lReturn.update(get_positional_entity_instantiations(sText, sMap))
    return lReturn


def get_positional_entity_instantiations(sText, sMap="port"):
    sText = reComment.sub(" ", sText)
    sText = reString.sub('""', sText)
    oMapPattern = reGenericMap if sMap == "generic" else rePortMap
    lReturn = set()
    for oMatch in reEntityInstantiation.finditer(sText):
        sStatement = get_statement(sText, oMatch.end())
        oMap = oMapPattern.search(sStatement)
        if oMap is None:
            continue
        sAssociations = get_parenthesized(sStatement, oMap.end())
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


def collect_port_modes(lFilenames):
    """
    Returns {"entity": {name: ports}, "component": {name: ports}} where ports is a tuple of (port name, mode)
    in declaration order, with lower case names and modes. A port without a mode has the mode "in".
    A name declared more than once with different ports maps to None.
    """
    dReturn = {"entity": {}, "component": {}}
    for sText in read_files(lFilenames):
        for sKind, sName, lPorts in get_port_orders(sText, bModes=True):
            dKind = dReturn[sKind]
            if sName in dKind and dKind[sName] != lPorts:
                dKind[sName] = None
            else:
                dKind[sName] = lPorts
    return dReturn


reMode = re.compile(r"\s*(in|out|inout|buffer|linkage)\b", re.IGNORECASE)


def get_port_orders(sText, bModes=False):
    """
    Returns (kind, name, ports) for each entity and component declaration in the text.
    ports is a tuple of lower case names, or of (name, mode) pairs with bModes.
    """
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
                lNames = [sName.strip().lower() for sName in sNames.split(",") if sName.strip()]
                if bModes:
                    oMode = reMode.match(sDeclaration.split(":", 1)[1])
                    sMode = oMode.group(1).lower() if oMode else "in"
                    lPorts.extend((sName, sMode) for sName in lNames)
                else:
                    lPorts.extend(lNames)
        lReturn.append((sKind, sName, tuple(lPorts)))
    return lReturn
