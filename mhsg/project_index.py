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
