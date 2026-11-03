# -*- coding: utf-8 -*-
"""
The description of a design, read from the design section of a configuration file:

    design:
      top: fifo_top
      standard: "08"
      libraries:
        - name: work
          files:
            - src/fifo_pkg.vhd
            - src/*.vhd
        - name: vendor
          files_from: ip/files.f
          exclude: ["*_tb.vhd"]
      generics:
        DEPTH: 16
      ghdl_options: [-frelaxed-rules]
"""

import fnmatch
import glob
import os

from mhsg import exceptions
from mhsg.design import black_box, vendors

STANDARDS = ("87", "93", "93c", "00", "02", "08", "19")


class Library:
    def __init__(self, sName, lFiles):
        self.name = sName
        self.files = lFiles


class Design:
    def __init__(self):
        self.top = None
        # The library the top entity is analyzed into; the last library if not given
        self.top_library = None
        self.architecture = None
        self.standard = "08"
        self.libraries = []
        self.generics = {}
        self.ghdl_options = []
        # Where GHDL and Yosys write their files; a temporary directory, removed after the run, if not given
        self.work_directory = None
        # Clock domain crossing constraints: clocks, clock_groups, inputs and waivers
        self.cdc = {}
        # Libraries of vendor component declarations, see vendors.py; also the first entries of libraries
        self.vendor_libraries = []
        # Declarations of the black boxes, see black_box.py
        self.black_boxes = black_box.Library()

    def all_files(self):
        return [sFile for oLibrary in self.libraries for sFile in oLibrary.files]


def from_configuration(dConfiguration):
    """Returns the Design described by the design section of a configuration, or raises a ConfigurationError."""
    dDesign = (dConfiguration or {}).get("design")
    if not isinstance(dDesign, dict):
        raise exceptions.ConfigurationError("ERROR: design analysis needs a design section in the configuration, see the design analysis documentation")
    oDesign = Design()
    oDesign.top = dDesign.get("top")
    if not oDesign.top:
        raise exceptions.ConfigurationError("ERROR: the design section needs a top entity, with the key top")
    oDesign.architecture = dDesign.get("architecture")
    oDesign.standard = str(dDesign.get("standard", "08"))
    if oDesign.standard not in STANDARDS:
        raise exceptions.ConfigurationError(f"ERROR: design standard {oDesign.standard} is not one of {', '.join(STANDARDS)}")
    for dLibrary in dDesign.get("libraries") or []:
        if not isinstance(dLibrary, dict) or "name" not in dLibrary:
            raise exceptions.ConfigurationError("ERROR: each design library needs a name and a list of files")
        lPatterns = read_file_list(dLibrary["files_from"]) if dLibrary.get("files_from") else []
        lExclude = [os.path.expandvars(str(s)) for s in dLibrary.get("exclude") or []]
        lPatterns = [s for s in lPatterns + list(dLibrary.get("files") or []) if not excluded(s, lExclude)]
        oDesign.libraries.append(Library(str(dLibrary["name"]), [s for s in expand_files(lPatterns) if not excluded(s, lExclude)]))
    if not oDesign.all_files():
        raise exceptions.ConfigurationError("ERROR: the design section lists no files that exist")
    # Vendor declarations are analyzed first, so the design can use them
    oDesign.vendor_libraries = vendors.resolve(dDesign.get("vendor_libraries"))
    oDesign.libraries = [Library(o.name, o.files) for o in oDesign.vendor_libraries] + oDesign.libraries
    oDesign.top_library = str(dDesign.get("top_library") or oDesign.libraries[-1].name)
    oDesign.generics = dict(dDesign.get("generics") or {})
    oDesign.ghdl_options = [str(s) for s in dDesign.get("ghdl_options") or []]
    oDesign.cdc = read_cdc(dDesign.get("cdc"))
    oDesign.black_boxes = black_box.from_design(dDesign)
    if dDesign.get("work_directory"):
        oDesign.work_directory = os.path.expandvars(str(dDesign["work_directory"]))
    return oDesign


CDC_KEYS = ("clocks", "clock_groups", "inputs", "waivers")


def read_cdc(dCdc):
    """Checks the cdc section of a design and returns it as a dictionary."""
    if dCdc is None:
        return {}
    if not isinstance(dCdc, dict):
        raise exceptions.ConfigurationError("ERROR: the cdc section of the design must be a map")
    lUnknown = sorted(str(s) for s in dCdc if s not in CDC_KEYS)
    if lUnknown:
        raise exceptions.ConfigurationError(f"ERROR: unknown keys in the cdc section of the design: {', '.join(lUnknown)}; expected {', '.join(CDC_KEYS)}")
    if not isinstance(dCdc.get("clocks") or {}, dict) or not isinstance(dCdc.get("inputs") or {}, dict):
        raise exceptions.ConfigurationError("ERROR: clocks and inputs in the cdc section map names to clocks")
    if any(not isinstance(l, list) for l in dCdc.get("clock_groups") or []):
        raise exceptions.ConfigurationError("ERROR: clock_groups in the cdc section is a list of lists of clock names")
    if any(not isinstance(d, dict) or "signal" not in d for d in dCdc.get("waivers") or []):
        raise exceptions.ConfigurationError("ERROR: each waiver in the cdc section needs a signal and a justification")
    return dict(dCdc)


def read_file_list(sFileList):
    """
    Returns the files named in a file list, one per line, such as the .f files of many projects.
    Lines starting with # or // are comments; environment variables are expanded; a relative path is relative to the
    list, or to the current directory when only that file exists, as for a variable that holds a relative path.
    """
    sFileList = os.path.expandvars(str(sFileList))
    if not os.path.isfile(sFileList):
        raise exceptions.ConfigurationError(f"ERROR: design file list {sFileList} does not exist")
    lReturn = []
    with open(sFileList, encoding="utf-8") as oFile:
        for sLine in oFile:
            sLine = sLine.strip()
            if not sLine or sLine.startswith(("#", "//")):
                continue
            sPath = os.path.expandvars(sLine)
            sBesideList = os.path.join(os.path.dirname(sFileList), sPath)
            if not os.path.isabs(sPath) and (os.path.exists(sBesideList) or not os.path.exists(sPath)):
                sPath = sBesideList
            lReturn.append(sPath)
    return lReturn


def excluded(sFile, lExclude):
    """Returns whether a file matches one of the exclude patterns, such as */test/* or *_tb.vhd."""
    sFile = os.path.normpath(os.path.expandvars(str(sFile)))
    return any(fnmatch.fnmatch(sFile, os.path.normpath(s)) or fnmatch.fnmatch(sFile, s) for s in lExclude)


def expand_files(lPatterns):
    """
    Returns the files matching the patterns, in the order of the patterns, which is the compile order.
    Environment variables are expanded; the files matching one glob pattern are sorted. Each file is listed once.
    """
    lReturn = []
    for sPattern in lPatterns:
        sExpanded = os.path.expandvars(str(sPattern))
        lMatches = sorted(glob.glob(sExpanded, recursive=True)) if glob.has_magic(sExpanded) else [sExpanded]
        for sFile in lMatches:
            if not os.path.isfile(sFile):
                raise exceptions.ConfigurationError(f"ERROR: design file {sFile} does not exist")
            sFile = os.path.normpath(sFile)
            if sFile not in lReturn:
                lReturn.append(sFile)
    return lReturn
