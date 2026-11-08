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

Verilog files are read as Verilog-2005, see language.py: names that are keywords only in SystemVerilog, such as logic
and bit, are names there.
"""

import os

import pyslang
from pyslang.parsing import PreprocessorOptions  # pylint: disable=import-error

from mhsg import language

# The version of the language slang reads Verilog files as
VERILOG_VERSION = pyslang.LanguageVersion.v1364_2005


def settings(dConfig):
    """Returns (defines as NAME or NAME=VALUE, include directories) from a configuration dictionary."""
    dConfig = dConfig or {}
    dSection = dConfig.get("systemverilog")
    if not isinstance(dSection, dict):
        dSection = dConfig.get("design") if isinstance(dConfig.get("design"), dict) else {}
    lDefines = [str(sName) if oValue is None else f"{sName}={oValue}" for sName, oValue in (dSection.get("defines") or {}).items()]
    lIncludes = [os.path.abspath(os.path.expandvars(str(s))) for s in dSection.get("include_directories") or []]
    return lDefines, lIncludes


def options(dConfig, sLanguage=None):
    """
    Returns the pyslang options bag for the preprocessor settings of a configuration, and for a Verilog file the
    version of the language, or None for none.
    """
    lDefines, lIncludes = settings(dConfig)
    bVerilog = sLanguage == language.VERILOG
    if not lDefines and not lIncludes and not bVerilog:
        return None
    oOptions = PreprocessorOptions()
    oOptions.predefines = lDefines
    oOptions.additionalIncludePaths = lIncludes
    if bVerilog:
        oOptions.languageVersion = VERILOG_VERSION
    return pyslang.Bag([oOptions])


def language_version(oOptions):
    """The language version of an options bag, or None for none, which is SystemVerilog."""
    oPreprocessor = getattr(oOptions, "preprocessorOptions", None) if oOptions is not None else None
    return oPreprocessor.languageVersion if oPreprocessor is not None else None
