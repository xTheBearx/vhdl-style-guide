# -*- coding: utf-8 -*-
"""
The preprocessor settings for SystemVerilog files, from the systemverilog section of the configuration:

    systemverilog:
      defines:
        SYNTHESIS:
        WIDTH: 8
      include_directories: [rtl/include, vendor/lowrisc_ip/ip/prim/rtl]

Without that section, the defines and include directories of the design section are used. With them, macros defined
in included files expand and `ifdef branches follow the defines, so fewer files have code slang cannot parse.
"""

import os

import pyslang
from pyslang.parsing import PreprocessorOptions  # pylint: disable=import-error


def settings(dConfig):
    """Returns (defines as NAME or NAME=VALUE, include directories) from a configuration dictionary."""
    dConfig = dConfig or {}
    dSection = dConfig.get("systemverilog")
    if not isinstance(dSection, dict):
        dSection = dConfig.get("design") if isinstance(dConfig.get("design"), dict) else {}
    lDefines = [str(sName) if oValue is None else f"{sName}={oValue}" for sName, oValue in (dSection.get("defines") or {}).items()]
    lIncludes = [os.path.abspath(os.path.expandvars(str(s))) for s in dSection.get("include_directories") or []]
    return lDefines, lIncludes


def options(dConfig):
    """Returns the pyslang options bag for the preprocessor settings of a configuration, or None for none."""
    lDefines, lIncludes = settings(dConfig)
    if not lDefines and not lIncludes:
        return None
    oOptions = PreprocessorOptions()
    oOptions.predefines = lDefines
    oOptions.additionalIncludePaths = lIncludes
    return pyslang.Bag([oOptions])
