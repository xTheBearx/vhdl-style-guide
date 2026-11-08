# -*- coding: utf-8 -*-
"""
Builds a description of every configuration option, which other programs can read to create an options dialog.

The description combines the rules, with their default values, and the option metadata in option_catalog.yaml.
The format is described in docs/options_description.rst.
"""

import copy
import json
import os
import re

from mhsg import rule_list, severity, version, vhdlFile, yaml_files
from mhsg.design import project

FORMAT_NAME = "mhsg-options"
FORMAT_VERSION = 1

DOCUMENTATION_URL = "https://github.com/xTheBearx/vhdl-style-guide/blob/master/docs/"

CATALOG_FILE = os.path.join(os.path.dirname(__file__), "option_catalog.yaml")
INDENT_FILE = os.path.join(os.path.dirname(__file__), "vhdlFile", "indent", "indent_config.yaml")

# Fields of an option definition, in the order they are written
DEFINITION_FIELDS = ("type", "label", "description", "values", "item_type", "nullable", "minimum", "maximum", "format")


def read_catalog():
    with open(CATALOG_FILE, encoding="utf-8") as oFile:
        return yaml_files.safe_load(oFile)["options"]


def build(lLocalRules=None):
    """
    Returns the description of all options as a dictionary.
    lLocalRules are local rule directories, whose rules are included.
    """
    dCatalog = read_catalog()
    oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), severity.create_list({}), lLocalRules, bAllLanguages=True)

    dDefinitions = {}
    lRules = []
    dGroups = {}
    for oRule in sorted(oRules.rules, key=lambda o: o.get_unique_id()):
        if oRule.deprecated or getattr(oRule, "proposed", False):
            continue
        lRules.append(describe_rule(oRule, dCatalog, dDefinitions))
        for sGroup in oRule.groups:
            dGroups.setdefault(sGroup, []).append(oRule.get_unique_id())

    return {
        "format": FORMAT_NAME,
        "format_version": FORMAT_VERSION,
        "mhsg_version": version.get_version(),
        "documentation_url": DOCUMENTATION_URL,
        "settings": describe_settings(),
        "rule_scopes": describe_rule_scopes(),
        "rule_groups": [{"name": sGroup, "rules": dGroups[sGroup]} for sGroup in sorted(dGroups)],
        "definitions": {sId: dDefinitions[sId] for sId in sorted(dDefinitions)},
        "rules": lRules,
    }


def describe_rule(oRule, dCatalog, dDefinitions):
    sId = oRule.get_unique_id()
    sDocLink = oRule.configuration_documentation_link
    lOptions = []
    for sOption in oRule.configuration:
        oDefault = get_default(oRule, sOption)
        sDefinition = add_definition(sOption, sDocLink, sId, oDefault, dCatalog, dDefinitions)
        lOptions.append({"name": sOption, "default": oDefault, "definition": sDefinition})
    dRule = {
        "id": sId,
        "alias": oRule.alias,
        "category": oRule.name,
        "groups": list(oRule.groups),
        "summary": get_summary(oRule),
        "documentation": f"{oRule.name}_rules.rst" if oRule.__module__.startswith("mhsg.rules.") else None,
        "options": lOptions,
    }
    if sDocLink is not None:
        dRule["option_documentation"] = sDocLink[: -len("_link")] + ".rst"
    return dRule


def get_default(oRule, sOption):
    if sOption == "severity":
        return oRule.severity.name
    oValue = getattr(oRule, sOption, None)
    if isinstance(oValue, tuple):
        oValue = list(oValue)
    return copy.deepcopy(oValue)


def add_definition(sOption, sDocLink, sRuleId, oDefault, dCatalog, dDefinitions):
    """
    Adds the definition of an option of a rule to dDefinitions, unless an identical one is there, and returns its identifier.
    """
    dEntry = dCatalog.get(sOption)
    if dEntry is None:
        dDefinition = infer_definition(sOption, oDefault)
        sId = sOption + ":" + sRuleId
    else:
        dDefinition = {sKey: dEntry[sKey] for sKey in DEFINITION_FIELDS if sKey in dEntry}
        sId = sOption
        dByDocLink = dEntry.get("by_doc_link", {})
        sDocKey = sDocLink if sDocLink is not None else "none"
        if sDocKey in dByDocLink:
            dDefinition.update(dByDocLink[sDocKey])
            sId = sOption + ":" + sDocKey.replace("configuring_", "").replace("_link", "")
        dByRule = dEntry.get("by_rule", {})
        if sRuleId in dByRule:
            dDefinition.update(dByRule[sRuleId])
            sId = sOption + ":" + sRuleId
    # An override can remove a field by setting it to null
    dDefinition = {sKey: dDefinition[sKey] for sKey in DEFINITION_FIELDS if dDefinition.get(sKey) is not None}
    if sId in dDefinitions and dDefinitions[sId] != dDefinition:
        raise ValueError(f"Option {sOption} has two different definitions named {sId}")
    dDefinitions[sId] = dDefinition
    return sId


def infer_definition(sOption, oDefault):
    """
    Returns a definition for an option without metadata, such as an option of a local rule, from its default value.
    """
    if isinstance(oDefault, bool):
        sType = "boolean"
    elif isinstance(oDefault, int):
        sType = "integer"
    elif isinstance(oDefault, list):
        sType = "list"
    else:
        sType = "string"
    dDefinition = {"type": sType, "label": sOption.replace("_", " ").capitalize(), "description": ""}
    if oDefault is None:
        dDefinition["nullable"] = True
    return dDefinition


def get_summary(oRule):
    """
    Returns the first paragraph of the rule documentation as plain text.
    """
    sDoc = oRule.__class__.__doc__ or ""
    lParagraph = []
    for sLine in sDoc.strip().splitlines():
        if not sLine.strip():
            break
        lParagraph.append(sLine.strip())
    return plain_text(" ".join(lParagraph))


def plain_text(sText):
    sText = re.sub(r":code:`([^`]*)`", r"\1", sText)
    sText = re.sub(r"\*\*([^*]*)\*\*", r"\1", sText)
    sText = re.sub(r"\*([^*]*)\*", r"\1", sText)
    sText = re.sub(r"``([^`]*)``", r"\1", sText)
    return sText


def describe_rule_scopes():
    return [
        {
            "path": ["rule", "<rule id or alias>"],
            "description": "Options of one rule. Takes precedence over group and global options.",
        },
        {
            "path": ["rule", "group", "<group name>"],
            "description": "Options for every rule in a rule group, see rule_groups. Takes precedence over global options.",
        },
        {
            "path": ["rule", "global"],
            "description": "Options for every rule that has an option of that name.",
        },
    ]


def describe_settings():
    """
    Returns the top level keys of a configuration file other than rule.
    """
    with open(INDENT_FILE, encoding="utf-8") as oFile:
        dIndent = yaml_files.safe_load(oFile)["indent"]
    from mhsg import config

    return [
        {
            "path": ["file_list"],
            "type": "list",
            "item_type": "string",
            "label": "Files to analyze",
            "description": "Files to analyze. Environment variables are expanded and glob patterns are supported.",
            "default": [],
        },
        {
            "path": ["file_rules"],
            "type": "file_rule_list",
            "label": "Rule options per file",
            "description": "A list of single key maps from a file name or glob pattern to a configuration with a rule key, applied to the files it matches.",
            "default": [],
        },
        {
            "path": ["index_file_list"],
            "type": "list",
            "item_type": "string",
            "label": "Index files",
            "description": "Files which are read, but not analyzed, so rules such as port_028 also see the instantiations in them.",
            "default": [],
        },
        {
            "path": ["local_rules"],
            "type": "list",
            "item_type": "string",
            "label": "Local rule directories",
            "description": "Directories with local rules to load.",
            "default": [],
        },
        {
            "path": ["lint"],
            "type": "boolean",
            "label": "Lint mode",
            "description": "Also run the lint checks, labelled with the checks of the rule set. The same as --lint.",
            "default": False,
        },
        {
            "path": ["lint_only"],
            "type": "boolean",
            "label": "Lint only",
            "description": "Run only the lint checks and the rules of the rule set. The same as --lint_only.",
            "default": False,
        },
        {
            "path": ["rule_set"],
            "type": "string",
            "label": "Rule set",
            "description": "Rule set for lint mode: a built in name such as do254, the path of a YAML file, or none for all lint rules without labels.",
            "default": "do254",
        },
        {
            "path": ["waivers"],
            "type": "waivers",
            "label": "Waivers",
            "description": "Findings accepted with a justification: each waiver names a rule (an identifier, alias or pattern) and a justification, and optionally a file pattern, a line or lines, a message pattern and a reviewer. Waived findings do not fail the run and are listed in the reports.",
            "default": [],
        },
        {
            "path": ["design", "top"],
            "type": "string",
            "nullable": True,
            "label": "Design top entity",
            "description": "The top entity of the design analyzed with --design.",
            "default": None,
        },
        {
            "path": ["design", "architecture"],
            "type": "string",
            "nullable": True,
            "label": "Design top architecture",
            "description": "The architecture of the top entity. GHDL chooses the last analyzed one when it is not set.",
            "default": None,
        },
        {
            "path": ["design", "standard"],
            "type": "enum",
            "values": list(project.STANDARDS),
            "label": "VHDL standard",
            "description": "The VHDL standard GHDL analyzes the design with.",
            "default": "08",
        },
        {
            "path": ["design", "libraries"],
            "type": "design_library_list",
            "label": "Design libraries",
            "description": "The libraries of the design in analysis order. Each has a name and files, a list of files and glob patterns, or files_from, a file listing them.",
            "default": [],
        },
        {
            "path": ["design", "top_library"],
            "type": "string",
            "nullable": True,
            "label": "Top library",
            "description": "The library of the top entity. The last library when it is not set.",
            "default": None,
        },
        {
            "path": ["design", "generics"],
            "type": "generic_map",
            "label": "Top generics",
            "description": "Values of the generics of the top entity, by name.",
            "default": {},
        },
        {
            "path": ["design", "work_directory"],
            "type": "string",
            "nullable": True,
            "label": "Design work directory",
            "description": "Keeps the files of GHDL and Yosys in this directory. A temporary directory is used and removed when it is not set.",
            "default": None,
        },
        {
            "path": ["design", "cdc"],
            "type": "cdc_constraints",
            "label": "Clock domain crossing constraints",
            "description": "Names of clock sources (clocks), groups of synchronous clocks (clock_groups), the clock domains of input ports and whether the bits of a vector input are independent (inputs), and crossings waived with a justification (waivers).",
            "default": {},
        },
        {
            "path": ["design", "vendor_libraries"],
            "type": "vendor_library_list",
            "label": "Vendor libraries",
            "description": "Vendor component declarations to analyze before the design, read from the vendor installation: xilinx, microchip, intel or lattice, or a library with its files.",
            "default": [],
        },
        {
            "path": ["design", "black_boxes"],
            "type": "black_box_map",
            "label": "Black box declarations",
            "description": "Maps black box types, such as vendor primitives, to the clock domain role of each port, or to an archetype. Every black box must be declared.",
            "default": {},
        },
        {
            "path": ["design", "black_box_libraries"],
            "type": "list",
            "item_type": "string",
            "label": "Black box libraries",
            "description": "YAML files with black_boxes and black_box_instances, shared between designs. The design section takes precedence.",
            "default": [],
        },
        {
            "path": ["design", "black_box_instances"],
            "type": "black_box_map",
            "label": "Black box instance declarations",
            "description": "Maps instance paths or patterns to declarations that take precedence over the declaration of their type.",
            "default": {},
        },
        {
            "path": ["design", "ghdl_options"],
            "type": "list",
            "item_type": "string",
            "label": "GHDL options",
            "description": "Extra options for GHDL, such as -fsynopsys.",
            "default": [],
        },
        {
            "path": ["linesep"],
            "type": "enum",
            "values": ["\n", "\r\n"],
            "nullable": True,
            "label": "Line separator",
            "description": "The line separator for fixed files. The platform default is used when it is not set.",
            "default": None,
        },
        {
            "path": ["severity"],
            "type": "severity_map",
            "label": "Custom severities",
            "description": "Maps names of custom severities to a map with a type key, error or warning. The names can then be used in the severity option of rules.",
            "default": {},
        },
        {
            "path": ["pragma", "patterns", "open"],
            "type": "list",
            "item_type": "string",
            "format": "regex",
            "label": "Opening pragmas",
            "description": "Regular expressions for comments which open a pragma region, such as -- synthesis translate_off.",
            "default": list(config.dPragmas["open"]),
        },
        {
            "path": ["pragma", "patterns", "close"],
            "type": "list",
            "item_type": "string",
            "format": "regex",
            "label": "Closing pragmas",
            "description": "Regular expressions for comments which close a pragma region, such as -- synthesis translate_on.",
            "default": list(config.dPragmas["close"]),
        },
        {
            "path": ["pragma", "patterns", "single"],
            "type": "list",
            "item_type": "string",
            "format": "regex",
            "label": "Single pragmas",
            "description": "Regular expressions for pragma comments which stand on their own.",
            "default": list(config.dPragmas["single"]),
        },
        {
            "path": ["indent", "options", "comment", "align_with_end_of_declarative_part"],
            "type": "boolean",
            "label": "Align comments with the end of a declarative part",
            "description": "Indent of a comment at the end of a declarative part: true uses the current indent level, false the next indent level.",
            "default": dIndent["options"]["comment"]["align_with_end_of_declarative_part"],
        },
        {
            "path": ["indent", "options", "comment", "align_with_end_of_statement_part"],
            "type": "boolean",
            "label": "Align comments with the end of a statement part",
            "description": "Indent of a comment at the end of a statement part: true uses the current indent level, false the next indent level.",
            "default": dIndent["options"]["comment"]["align_with_end_of_statement_part"],
        },
        {
            "path": ["indent", "tokens"],
            "type": "indent_table",
            "label": "Indent of tokens",
            "description": (
                "The indent of each token (token) and of the lines after it (after), by token group and token name. "
                "A value is an indent level, current to keep the current level, or a string such as +1 or -1 relative to the current level."
            ),
            "default": dIndent["tokens"],
        },
    ]


def write(sFileName, lLocalRules=None):
    with open(sFileName, "w", encoding="utf-8") as oFile:
        oFile.write(to_json(build(lLocalRules)))


def to_json(dDescription):
    return json.dumps(dDescription, indent=2, ensure_ascii=False) + "\n"
