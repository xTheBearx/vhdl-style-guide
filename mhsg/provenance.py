# -*- coding: utf-8 -*-
"""
The record of a run that reports carry, so a result can be reproduced and audited: the versions of mhsg and of the
tools it used, the command line, the configuration files and rule sets with their digests.
"""

import hashlib
import importlib.metadata
import json
import platform
import sys

from mhsg import version


def file_digest(sFileName):
    """Returns the SHA-256 digest of a file, or None if it cannot be read."""
    try:
        with open(sFileName, "rb") as oFile:
            return hashlib.sha256(oFile.read()).hexdigest()
    except OSError:
        return None


def package_version(sName):
    try:
        return importlib.metadata.version(sName)
    except importlib.metadata.PackageNotFoundError:
        return None


def record(commandLineArguments, oConfig, oTools=None):
    """
    Returns the record of this run as a dictionary. oTools, the GHDL and Yosys found for design analysis, adds their
    versions.
    """
    dRecord = {
        "mhsg": version.get_version(),
        "python": platform.python_version(),
        "pyslang": package_version("pyslang"),
        "command_line": list(sys.argv[1:]),
        "configuration_files": [{"file": s, "sha256": file_digest(s)} for s in getattr(commandLineArguments, "configuration", None) or []],
        # The configuration after merging the files, so settings given in several files are covered too
        "configuration_sha256": hashlib.sha256(json.dumps(oConfig.dConfig or {}, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
        "lint_mode": getattr(oConfig, "lint_mode", None),
        "rule_sets": [],
    }
    oRuleSet = getattr(oConfig, "rule_set", None)
    if oRuleSet is not None:
        dRecord["rule_sets"] = [{"name": o.name, "version": o.version, "sha256": file_digest(o.filename)} for o in oRuleSet.all_sets()]
    if getattr(commandLineArguments, "local_rules", None):
        dRecord["local_rules"] = commandLineArguments.local_rules
    if dRecord["lint_mode"] is not None:
        # Verilator lints SystemVerilog files in lint mode, see sv_lint_011
        from mhsg.svFile import verilator  # pylint: disable=import-outside-toplevel

        sVerilator = verilator.find(oConfig.dConfig)
        dRecord["verilator"] = verilator.version(sVerilator) if sVerilator else None
    if oTools is not None:
        dRecord["ghdl"] = oTools.ghdl_version or None
        dRecord["yosys"] = oTools.yosys_version or None
        dRecord["yosys_slang"] = bool(oTools.slang)
    return dRecord


def summary(dRecord):
    """Returns the record as lines of text, for text reports."""
    lTools = [f"mhsg {dRecord['mhsg']}", f"Python {dRecord['python']}"]
    for sKey, sName in (("pyslang", "pyslang"), ("verilator", "Verilator"), ("ghdl", "GHDL"), ("yosys", "Yosys")):
        if dRecord.get(sKey):
            # The versions some tools give start with their name, such as GHDL 4.1.0
            sVersion = str(dRecord[sKey])
            lTools.append(sVersion if sVersion.lower().startswith(sName.lower()) else f"{sName} {sVersion}")
    lLines = ["Tools: " + ", ".join(lTools)]
    for dFile in dRecord["configuration_files"]:
        lLines.append(f"Configuration: {dFile['file']} (sha256 {dFile['sha256']})")
    for dRuleSet in dRecord["rule_sets"]:
        lLines.append(f"Rule set: {dRuleSet['name']} version {dRuleSet['version']} (sha256 {dRuleSet['sha256']})")
    lLines.append("Command line: " + " ".join(dRecord["command_line"]))
    return lLines


def properties(dRecord):
    """Returns the record as (name, value) pairs, for the properties of a JUnit report."""
    lReturn = [("mhsg.version", dRecord["mhsg"]), ("python.version", dRecord["python"])]
    for sKey in ("pyslang", "verilator", "ghdl", "yosys"):
        if dRecord.get(sKey):
            lReturn.append((sKey + ".version", dRecord[sKey]))
    lReturn.append(("command_line", " ".join(dRecord["command_line"])))
    for dFile in dRecord["configuration_files"]:
        lReturn.append(("configuration_file", f"{dFile['file']} sha256:{dFile['sha256']}"))
    lReturn.append(("configuration.sha256", dRecord["configuration_sha256"]))
    if dRecord["lint_mode"]:
        lReturn.append(("lint_mode", dRecord["lint_mode"]))
    for dRuleSet in dRecord["rule_sets"]:
        lReturn.append(("rule_set", f"{dRuleSet['name']} version {dRuleSet['version']} sha256:{dRuleSet['sha256']}"))
    return lReturn
