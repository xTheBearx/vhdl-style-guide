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
      generics:
        DEPTH: 16
      ghdl_options: [-frelaxed-rules]
"""

import glob
import os

from mhsg import exceptions

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
        oDesign.libraries.append(Library(str(dLibrary["name"]), expand_files(lPatterns + list(dLibrary.get("files") or []))))
    if not oDesign.all_files():
        raise exceptions.ConfigurationError("ERROR: the design section lists no files that exist")
    oDesign.top_library = str(dDesign.get("top_library") or oDesign.libraries[-1].name)
    oDesign.generics = dict(dDesign.get("generics") or {})
    oDesign.ghdl_options = [str(s) for s in dDesign.get("ghdl_options") or []]
    return oDesign


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
            if sFile not in lReturn:
                lReturn.append(sFile)
    return lReturn
