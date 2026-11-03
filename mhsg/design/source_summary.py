# -*- coding: utf-8 -*-
"""
What design analysis needs to know of a VHDL source file: its processes, the lines they span, whether they are
clocked, and the lines of their signal assignments; and where the statements of each architecture start.

Parsing a VHDL file is the slowest part of design analysis on a large design, so the summary of each file is kept in
a cache directory, under the hash of the file's contents, the version of MHSG and its parsing code, and read from there
while the file and MHSG are unchanged. The cache is in $MHSG_CACHE_DIRECTORY, else $XDG_CACHE_HOME/mhsg, else ~/.cache/mhsg; MHSG_CACHE_DIRECTORY
set to an empty value turns it off.
"""

import hashlib
import json
import os

from mhsg import version, vhdlFile
from mhsg.lint import model

# Changes when the summary changes, so summaries of an older form are not read
FORMAT = 1

# The code that parses VHDL and makes the summary: its digest is part of the key, as a development install keeps its
# version while the code changes
CODE_DIRECTORIES = ("vhdlFile", "lint", "token")
_sCodeDigest = None


def code_digest():
    """The digest of the code that makes the summaries, computed once."""
    global _sCodeDigest  # pylint: disable=global-statement
    if _sCodeDigest is None:
        oHash = hashlib.sha256()
        sRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lFiles = [os.path.abspath(__file__)]
        for sDirectory in CODE_DIRECTORIES:
            for sPath, _, lNames in os.walk(os.path.join(sRoot, sDirectory)):
                lFiles.extend(os.path.join(sPath, s) for s in lNames if s.endswith(".py"))
        for sFile in sorted(lFiles):
            with open(sFile, "rb") as oFile:
                oHash.update(oFile.read())
        _sCodeDigest = oHash.hexdigest()
    return _sCodeDigest


class Process:
    def __init__(self, iLine, iEndLine, bClocked, lAssignments):
        self.line = iLine
        self.end_line = iEndLine
        self.clocked = bClocked
        # (lower case base name, line) of each signal assignment, in order
        self.assignments = lAssignments


class Architecture:
    def __init__(self, lProcesses, iFirstStatement):
        self.processes = lProcesses
        # The line of the first process, concurrent assignment or instance, or None
        self.first_statement = iFirstStatement


def summarize(oFile):
    """Returns the Architecture list of a parsed VHDL file."""
    lReturn = []
    for oArchitecture in oFile.get_lint_model().architectures:
        lProcesses = [
            Process(o.line, o.end_line, o.clock is not None, [(a.base, a.line) for a in model.assignments(o.statements)]) for o in oArchitecture.processes
        ]
        lLines = [o.line for o in oArchitecture.processes + oArchitecture.assignments + oArchitecture.instances]
        lReturn.append(Architecture(lProcesses, min(lLines) if lLines else None))
    return lReturn


def to_json(lArchitectures):
    return [
        {"first_statement": o.first_statement, "processes": [[p.line, p.end_line, p.clocked, [list(a) for a in p.assignments]] for p in o.processes]}
        for o in lArchitectures
    ]


def from_json(lData):
    return [Architecture([Process(p[0], p[1], p[2], [tuple(a) for a in p[3]]) for p in d["processes"]], d["first_statement"]) for d in lData]


def cache_directory():
    """The directory of the cache, or None if it is turned off."""
    if "MHSG_CACHE_DIRECTORY" in os.environ:
        return os.environ["MHSG_CACHE_DIRECTORY"] or None
    sBase = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(sBase, "mhsg")


def load(sFileName):
    """Returns the Architecture list of a VHDL file, from the cache when the file is unchanged, or None if it cannot be read or parsed."""
    try:
        with open(sFileName, "rb") as oFile:
            bContents = oFile.read()
    except OSError:
        return None
    sKey = hashlib.sha256(bContents + f"\0{version.get_version()}\0{FORMAT}\0{code_digest()}".encode()).hexdigest()
    sDirectory = cache_directory()
    sCacheFile = os.path.join(sDirectory, "design", sKey[:2], sKey + ".json") if sDirectory else None
    if sCacheFile and os.path.isfile(sCacheFile):
        try:
            with open(sCacheFile, encoding="utf-8") as oFile:
                return from_json(json.load(oFile))
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            pass
    try:
        lLines, eError = vhdlFile.utils.read_vhdlfile(sFileName)
        if eError:
            return None
        lArchitectures = summarize(vhdlFile.vhdlFile(lLines))
    except Exception:  # pylint: disable=broad-except
        return None
    if sCacheFile:
        try:
            os.makedirs(os.path.dirname(sCacheFile), exist_ok=True)
            sTemporary = sCacheFile + f".{os.getpid()}.tmp"
            with open(sTemporary, "w", encoding="utf-8") as oFile:
                json.dump(to_json(lArchitectures), oFile)
            os.replace(sTemporary, sCacheFile)
        except OSError:
            pass
    return lArchitectures
