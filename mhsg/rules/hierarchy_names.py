# -*- coding: utf-8 -*-
"""
The comparison of a signal with the port it connects to, for DO-254 DR9: lint_040 for VHDL and sv_module_018 for
SystemVerilog read the same defaults and compare names the same way, so the check means the same in both languages.
"""

# Prefixes that mark the direction or kind of a name
STRIP_PREFIXES = ("i_", "o_", "io_", "s_", "r_", "w_")

# Suffixes that mark the direction or kind of a name: those of port names written by direction, as sv_naming_016
# asks for (_i, _o and _io, with _n or n before them for active low ports), then those of signals and registers
STRIP_SUFFIXES = ("_i", "_o", "_io", "_ni", "_no", "_nio", "_n_i", "_n_o", "_n_io", "_s", "_r", "_n", "_d", "_q", "_reg", "_sig")


def stem(sName, lPrefixes, lSuffixes):
    """The name in lower case without one of the prefixes and one of the suffixes, the longest that fits."""
    sName = sName.lower()
    for sPrefix in sorted(lPrefixes, key=len, reverse=True):
        if sName.startswith(sPrefix.lower()) and len(sName) > len(sPrefix):
            sName = sName[len(sPrefix) :]
            break
    for sSuffix in sorted(lSuffixes, key=len, reverse=True):
        if sName.endswith(sSuffix.lower()) and len(sName) > len(sSuffix):
            sName = sName[: -len(sSuffix)]
            break
    return sName
