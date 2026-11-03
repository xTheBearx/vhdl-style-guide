# -*- coding: utf-8 -*-
"""
Checks the top entity of a design before GHDL runs.

GHDL elaborates a top entity whose generic has no default value and no value from the design section with the
leftmost value of its type, without a message, so the design would be analyzed for a configuration nobody chose.
"""

import os
import re

from mhsg import parser, vhdlFile
from mhsg.token import (
    entity_declaration,
    generic_clause,
    interface_constant_declaration,
    interface_list,
    interface_unknown_declaration,
    type_mark,
)

GENERIC_IDENTIFIERS = (interface_unknown_declaration.identifier, interface_constant_declaration.identifier)


def find_top(oDesign):
    """Returns (file name, parsed file) of the top entity, looked up in the top library, the last declaration first, or (None, None)."""
    reEntity = re.compile(r"\bentity\s+" + re.escape(oDesign.top) + r"\s+is\b", re.IGNORECASE)
    lFiles = [s for o in oDesign.libraries if o.name.lower() == oDesign.top_library.lower() for s in o.files]
    for sFile in reversed(lFiles):
        try:
            with open(sFile, encoding="utf-8", errors="replace") as oFile:
                sText = oFile.read()
        except OSError:
            continue
        if not reEntity.search(sText):
            continue
        lLines, eError = vhdlFile.utils.read_vhdlfile(sFile)
        if eError:
            return None, None
        return sFile, vhdlFile.vhdlFile(lLines)
    return None, None


def missing_generics(oDesign):
    """
    Returns (file, line, generic name) for each generic of the top entity without a default value that the design
    section does not set. The top entity is looked up in the files of the top library, the last declaration first.
    """
    sFile, oFile = find_top(oDesign)
    if oFile is None:
        return []
    setSet = {s.lower() for s in oDesign.generics}
    return [(sFile, iLine, sName) for sName, iLine in generics_without_default(oFile, oDesign.top) if sName.lower() not in setSet]


def unknown_generics(oDesign):
    """Returns (file, line, name) for each generic set in the design section that the top entity does not declare."""
    sFile, oFile = find_top(oDesign)
    if oFile is None:
        return []
    setDeclared = {s.lower() for d in generic_declarations(oFile, oDesign.top) for s, _ in d["names"]}
    iLine = next((d["names"][0][1] for d in generic_declarations(oFile, oDesign.top)), 0)
    return [(sFile, iLine, s) for s in oDesign.generics if s.lower() not in setDeclared]


def generic_declarations(oFile, sEntity):
    """
    Returns a dictionary for each generic declaration of an entity in a parsed file, with its names and lines,
    its type mark, the token indexes of its default value (assignment to the end) and the index of the token that ends it.
    """
    lReturn = []
    bEntity = False
    bGenerics = False
    dDeclaration = None
    iLine = 1
    for iIndex, oToken in enumerate(oFile.lAllObjects):
        if isinstance(oToken, parser.carriage_return):
            iLine += 1
            continue
        if isinstance(oToken, entity_declaration.identifier):
            bEntity = oToken.get_value().lower() == sEntity.lower()
            continue
        if not bEntity:
            continue
        if isinstance(oToken, (entity_declaration.end_keyword, entity_declaration.is_keyword)) and bGenerics:
            break
        if isinstance(oToken, generic_clause.open_parenthesis):
            bGenerics = True
            continue
        if not bGenerics:
            continue
        if dDeclaration is None:
            dDeclaration = {"names": [], "type": None, "default": None, "end": None}
        if isinstance(oToken, GENERIC_IDENTIFIERS):
            dDeclaration["names"].append((oToken.get_value(), iLine))
        elif isinstance(oToken, type_mark.name) and dDeclaration["type"] is None:
            dDeclaration["type"] = oToken.get_value().lower()
        elif type(oToken).__name__ == "assignment" and dDeclaration["default"] is None:
            dDeclaration["default"] = iIndex
        elif isinstance(oToken, (interface_list.semicolon, generic_clause.close_parenthesis)):
            dDeclaration["end"] = iIndex
            if dDeclaration["names"]:
                lReturn.append(dDeclaration)
            dDeclaration = None
            if isinstance(oToken, generic_clause.close_parenthesis):
                break
    return lReturn


def generics_without_default(oFile, sEntity):
    """Returns (name, line) for each generic of an entity in a parsed file that has no default value."""
    return [tName for d in generic_declarations(oFile, sEntity) if d["default"] is None for tName in d["names"]]


def real_literal(oValue):
    """Returns a value as a VHDL real literal, such as 100000000.0 or 1.0e+20."""
    sValue = repr(float(oValue))
    sMantissa, _, sExponent = sValue.partition("e")
    if "." not in sMantissa:
        sMantissa += ".0"
    return sMantissa + ("e" + sExponent if sExponent else "")


def time_literal(oValue):
    """Returns a value as a VHDL physical literal, such as 10 ns, from 10 ns, 10ns or a number of nanoseconds."""
    if isinstance(oValue, (int, float)) and not isinstance(oValue, bool):
        return f"{oValue} ns"
    oMatch = re.fullmatch(r"\s*([0-9][0-9_.eE+-]*)\s*([A-Za-z]+)\s*", str(oValue))
    return f"{oMatch.group(1)} {oMatch.group(2)}" if oMatch else str(oValue)


# The types of generics GHDL cannot set from the command line, and how their values are written in VHDL
PATCHED_TYPES = {"real": real_literal, "time": time_literal, "delay_length": time_literal}

# The types whose values GHDL wants quoted as character literals on the command line, such as '1'
CHARACTER_TYPES = ("std_logic", "std_ulogic", "bit", "character")


def generic_types(oDesign):
    """Returns {lower case name: lower case type mark} of the generics of the top entity, or {}."""
    _, oFile = find_top(oDesign)
    if oFile is None:
        return {}
    return {s.lower(): d["type"] for d in generic_declarations(oFile, oDesign.top) for s, _ in d["names"] if d["type"]}


def patch_real_generics(oDesign, sDirectory):
    """
    GHDL cannot set a generic of type real or time from the command line. Writes a copy of the file of the top entity
    in which the values of those generics set in the design section are the defaults, keeping every line in place.
    Returns (original file, copy, names of the patched generics), or None if there is nothing to patch.
    """
    sFile, oFile = find_top(oDesign)
    if oFile is None:
        return None
    dValues = {s.lower(): o for s, o in oDesign.generics.items()}
    lPatched = []
    for dDeclaration in generic_declarations(oFile, oDesign.top):
        lNames = [s.lower() for s, _ in dDeclaration["names"]]
        if dDeclaration["type"] not in PATCHED_TYPES or len(lNames) != 1 or lNames[0] not in dValues:
            continue
        iStart = dDeclaration["default"] if dDeclaration["default"] is not None else dDeclaration["end"]
        for iIndex in range(iStart, dDeclaration["end"]):
            if not isinstance(oFile.lAllObjects[iIndex], parser.carriage_return):
                oFile.lAllObjects[iIndex].set_value("")
        sValue = PATCHED_TYPES[dDeclaration["type"]](dValues[lNames[0]])
        oFile.lAllObjects[iStart].set_value(" := " + sValue + oFile.lAllObjects[iStart].get_value())
        lPatched.append(dDeclaration["names"][0][0])
    if not lPatched:
        return None
    sCopy = os.path.join(sDirectory, "patched", os.path.basename(sFile))
    os.makedirs(os.path.dirname(sCopy), exist_ok=True)
    with open(sCopy, "w", encoding="utf-8") as oCopy:
        oCopy.write("".join("\n" if isinstance(o, parser.carriage_return) else o.get_value() for o in oFile.lAllObjects))
    return sFile, sCopy, lPatched
