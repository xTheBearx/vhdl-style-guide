# -*- coding: utf-8 -*-
"""
Lint of the Verilog and SystemVerilog files of a run as one design.

In lint mode, the Verilog and SystemVerilog files of a run, those given with --index_files and those listed under files in the
systemverilog section of the configuration are compiled together once, before the files are checked. Each file then
gets the warnings slang found in it, with the modules, packages and macros of the other files known: unused,
undriven and implicit signals are checked wherever everything a file uses is in the run, and the connections of
instances are checked against the modules they instantiate.
"""

import hashlib
import os
import re

import pyslang
from pyslang import analysis, ast  # pylint: disable=import-error
from pyslang.syntax import SyntaxNode, SyntaxTree  # pylint: disable=import-error

from mhsg import config, language
from mhsg.rules.sv_lint import diagnostics, verilator_rule
from mhsg.svFile import lint, preprocessor, verilator
from mhsg.vhdlFile import utils


def text_hash(sText):
    return hashlib.sha1(sText.encode("utf-8", errors="surrogateescape")).hexdigest()


def file_text(sFileName):
    """The text of a file as svFile parses it: its lines without their line ends, each ended with a new line."""
    lLines, eError = utils.read_vhdlfile(sFileName)
    if eError:
        return None
    return "\n".join(lLines) + "\n" if lLines else ""


def files_of_run(lFiles, dConfig):
    """
    The Verilog and SystemVerilog files among the files of a run, then those listed under files in the systemverilog
    section.
    """
    lReturn = []
    dSection = (dConfig or {}).get("systemverilog") or {}
    lExtra = []
    for sPattern in dSection.get("files") or [] if isinstance(dSection, dict) else []:
        sPattern = os.path.expandvars(str(sPattern))
        lExtra.extend(config.glob_filenames(sPattern) or [sPattern])
    for sFile in list(lFiles) + lExtra:
        sPath = os.path.abspath(sFile)
        if language.is_verilog(sFile) and os.path.isfile(sPath) and sPath not in lReturn:
            lReturn.append(sPath)
    return lReturn


def verilator_enabled(oConfig):
    """
    Whether a rule that reports Verilator's warnings, sv_lint_011 to sv_lint_013, is enabled in this lint run: by the
    configuration, or else by lint mode without a rule set, which enables every lint rule, or by a rule set that lists
    it.
    """
    return any(rule_enabled(oConfig, sRule) for sRule in verilator_rule.RULES)


def rule_enabled(oConfig, sRule):
    """Whether a lint rule is enabled in this lint run, by the configuration, or by lint mode and the rule set."""
    dRule = ((getattr(oConfig, "dConfig", None) or {}).get("rule") or {}).get(sRule) or {}
    if isinstance(dRule, dict) and "disable" in dRule:
        return not dRule["disable"]
    oRuleSet = getattr(oConfig, "rule_set", None)
    if oRuleSet is None:
        return True
    return any(sRule in oCheck.rules for oSet in oRuleSet.all_sets() for oCheck in oSet.checks)


def collect(lFiles, dConfig, bVerilator=False):
    """
    Compiles the Verilog and SystemVerilog files of a run together and returns {absolute file name: entry}, where an entry holds
    the hash of the text compiled, the warnings as (offset, name, message), and whether the file uses something
    unknown to the run.
    """
    lPaths = files_of_run(lFiles, dConfig)
    if not lPaths:
        return {}
    oSourceManager = pyslang.SourceManager()
    oCompilation = ast.Compilation()
    dBuffers = {}
    lTrees = []
    # Every file gets its buffer before any is parsed, so a file another one includes is read once, as it is here
    lBuffers = []
    dTexts = {}
    for sPath in lPaths:
        sText = file_text(sPath)
        if sText is None:
            continue
        oBuffer = oSourceManager.assignText(sPath, sText)
        lBuffers.append(oBuffer)
        dBuffers[oBuffer.id.id] = (sPath, text_hash(sText))
        dTexts[sPath] = sText
    lFiles = []
    for oBuffer in lBuffers:
        # Each file is parsed in its language: Verilog files as Verilog-2005, see language.py
        oOptions = preprocessor.options(dConfig, language.of_file(dBuffers[oBuffer.id.id][0], dConfig))
        oTree = SyntaxTree.fromBuffer(oBuffer, oSourceManager, oOptions) if oOptions is not None else SyntaxTree.fromBuffer(oBuffer, oSourceManager)
        oCompilation.addSyntaxTree(oTree)
        lTrees.append(oTree)
        lFiles.append((dBuffers[oBuffer.id.id][0], oTree))
    lDiagnostics = list(oCompilation.getAllDiagnostics())
    oCompilation.freeze()
    oAnalysisOptions = analysis.AnalysisOptions()
    oAnalysisOptions.flags = analysis.AnalysisFlags.CheckUnused
    oAnalysis = analysis.AnalysisManager(oAnalysisOptions)
    oAnalysis.analyze(oCompilation)
    lDiagnostics.extend(oAnalysis.getDiagnostics())
    oEngine = pyslang.DiagnosticEngine(oCompilation.sourceManager)
    # The enum types of the run, shared by the entries of all files, see enum_types
    dEnums = enum_types(lTrees)
    # How often the run instantiates each module, shared the same way, see sv_module_018
    dInstances = instance_counts(oInstance for oTree in lTrees for oInstance in walk(oTree.root, "HierarchicalInstance"))
    dReturn = {sPath: {"hash": sHash, "diagnostics": [], "incomplete": False, "enums": dEnums, "instances": dInstances} for sPath, sHash in dBuffers.values()}
    for oTree in lTrees:
        lDiagnostics.extend(oTree.diagnostics)
    for oDiagnostic in lDiagnostics:
        oLocation = lint.original_location(oSourceManager, oDiagnostic.location)
        tFile = dBuffers.get(oLocation.buffer.id)
        if tFile is None:
            continue
        dEntry = dReturn[tFile[0]]
        sName = lint.diagnostic_name(oDiagnostic)
        if oDiagnostic.isError():
            if sName in lint.UNKNOWN:
                dEntry["incomplete"] = True
            continue
        tDiagnostic = (oLocation.offset, sName, oEngine.formatMessage(oDiagnostic))
        if tDiagnostic not in dEntry["diagnostics"]:
            dEntry["diagnostics"].append(tDiagnostic)
    for sPath, iOffset, sName, sMessage in parameter_diagnostics(lFiles) + macro_diagnostics(lFiles, dTexts):
        tDiagnostic = (iOffset, sName, sMessage)
        if tDiagnostic not in dReturn[sPath]["diagnostics"]:
            dReturn[sPath]["diagnostics"].append(tDiagnostic)
    # Verilator's warnings, when sv_lint_011 is enabled and Verilator installed, see verilator.py
    sVerilator = verilator.find(dConfig) if bVerilator else None
    if sVerilator is not None:
        for sPath, iOffset, sName, sMessage in verilator.lint(sVerilator, lFiles, dConfig, dTexts):
            tDiagnostic = (iOffset, sName, sMessage)
            if tDiagnostic not in dReturn[sPath]["diagnostics"]:
                dReturn[sPath]["diagnostics"].append(tDiagnostic)
    return dReturn


def enum_types(lTrees):
    """
    The enum types the files of a run declare with typedef, for rules that look at a variable of a type declared in
    another file, such as the state of a state machine typed in a package: {"qualified": {name: values}, "bare":
    {name: (qualified name, values)}}. A type in a package is qualified with the package, pkg::state_e, and also found
    by its bare name when no other package of the run declares that name; a type outside packages has its bare name.
    """
    dQualified = {}
    dBare = {}
    for oTree in lTrees:
        for oTypedef in walk(oTree.root, "TypedefDeclaration"):
            if oTypedef.type is None or oTypedef.type.kind.name != "EnumType":
                continue
            sName = oTypedef.name.rawText
            lValues = [o.name.rawText for o in oTypedef.type.members if isinstance(o, SyntaxNode)]
            oPackage = next((o for o in ancestors(oTypedef) if o.kind.name == "PackageDeclaration"), None)
            sQualified = f"{oPackage.header.name.rawText}::{sName}" if oPackage is not None else sName
            dQualified[sQualified] = lValues
            if sName in dBare and dBare[sName] is not None and dBare[sName][0] != sQualified:
                dBare[sName] = None
            elif sName not in dBare:
                dBare[sName] = (sQualified, lValues)
    return {"qualified": dQualified, "bare": {s: t for s, t in dBare.items() if t is not None}}


def instance_counts(lInstances):
    """
    {module name: number of instances} of instances, HierarchicalInstance nodes. An instance array, or an instance in
    a loop generate, counts as two: it makes more than one instance of the module.
    """
    dReturn = {}
    for oInstance in lInstances:
        oInstantiation = oInstance.parent
        if oInstantiation is None or oInstantiation.kind.name != "HierarchyInstantiation":
            continue
        sModule = oInstantiation.type.valueText
        bMany = (oInstance.decl is not None and len(syntax_nodes(oInstance.decl.dimensions)) > 0) or any(
            o.kind.name == "LoopGenerate" for o in ancestors(oInstance)
        )
        dReturn[sModule] = dReturn.get(sModule, 0) + (2 if bMany else 1)
    return dReturn


def ancestors(oNode):
    oParent = oNode.parent
    while oParent is not None:
        yield oParent
        oParent = oParent.parent


def syntax_nodes(oNode):
    """The nodes among the children of a node, without the tokens."""
    return [o for o in oNode if isinstance(o, SyntaxNode)]


def walk(oNode, sKind):
    """Yields the nodes of a kind under a node, in the order of the text."""
    lStack = [oNode]
    while lStack:
        oCurrent = lStack.pop()
        if oCurrent.kind.name == sKind:
            yield oCurrent
        lStack.extend(reversed(syntax_nodes(oCurrent)))


def module_parameters(oModule):
    """
    The (name, token, overridable) of the parameters of a module: in its parameter port list, then in its body. With a
    parameter port list, the parameters of the body are local, as localparam declarations always are.
    """
    lReturn = []
    oList = oModule.header.parameters
    bHeader = oList is not None
    lDeclarations = syntax_nodes(oList.declarations) if bHeader else []
    sKeyword = "parameter"
    for oDeclaration in lDeclarations:
        # A declaration without a keyword continues the kind of the one before it
        sKeyword = oDeclaration.keyword.valueText or sKeyword
        for oDeclarator in syntax_nodes(oDeclaration.declarators):
            lReturn.append((oDeclarator.name.valueText, oDeclarator.name, sKeyword == "parameter"))
    for oStatement in walk(oModule, "ParameterDeclarationStatement"):
        oDeclaration = oStatement.parameter
        bOverridable = oDeclaration.keyword.valueText == "parameter" and not bHeader
        for oDeclarator in syntax_nodes(oDeclaration.declarators):
            lReturn.append((oDeclarator.name.valueText, oDeclarator.name, bOverridable))
    return lReturn


def parameter_diagnostics(lFiles):
    """
    Returns (file, offset, name, message) of the instances that set some but not all of the parameters of a module of
    the run, and of the parameters named like one of another module of the run.
    """
    lReturn = []
    dModules = {}
    lModules = []
    for sPath, oTree in lFiles:
        for oModule in walk(oTree.root, "ModuleDeclaration"):
            sName = oModule.header.name.valueText
            lParameters = module_parameters(oModule)
            dModules.setdefault(sName, lParameters)
            lModules.append((sPath, sName, oModule, lParameters))
    dFirst = {}
    for sPath, sName, _, lParameters in lModules:
        for sParameter, oToken, _ in lParameters:
            sFirst = dFirst.setdefault(sParameter, sName)
            if sFirst != sName:
                lReturn.append((sPath, oToken.location.offset, diagnostics.REUSED_PARAMETER, f"Parameter {sParameter} is also declared in module {sFirst}"))
    for sPath, sName, oModule, _ in lModules:
        for oInstance in walk(oModule, "HierarchyInstantiation"):
            sType = oInstance.type.valueText
            if oInstance.parameters is None or sType not in dModules:
                continue
            lNames = [s for s, _, b in dModules[sType] if b]
            lAssignments = syntax_nodes(oInstance.parameters.parameters)
            if not lAssignments:
                continue
            if all(o.kind.name == "NamedParamAssignment" for o in lAssignments):
                setGiven = {o.name.valueText for o in lAssignments}
                lMissing = [s for s in lNames if s not in setGiven]
            else:
                lMissing = lNames[len(lAssignments) :]
            if lMissing:
                iGiven = len(lNames) - len(lMissing)
                sMessage = f"Instance of {sType} sets {iGiven} of its {len(lNames)} parameters; also set {', '.join(lMissing)}"
                lReturn.append((sPath, oInstance.getFirstToken().location.offset, diagnostics.PARTIAL_OVERRIDE, sMessage))
    return lReturn


# Compiler directives, which are not macros
DIRECTIVES = {
    "begin_keywords",
    "celldefine",
    "default_nettype",
    "define",
    "else",
    "elsif",
    "end_keywords",
    "endcelldefine",
    "endif",
    "ifdef",
    "ifndef",
    "include",
    "line",
    "nounconnected_drive",
    "pragma",
    "resetall",
    "timescale",
    "unconnected_drive",
    "undef",
    "undefineall",
    "__FILE__",
    "__LINE__",
}
reComment = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
reDefine = re.compile(r"`define\s+(\w+)")
reMacro = re.compile(r"`(\w+)")
DESIGN_UNITS = ("ModuleDeclaration", "InterfaceDeclaration", "ProgramDeclaration")


def without_comments(sText):
    """The text with its comments replaced by spaces, so offsets do not change."""
    return reComment.sub(lambda o: re.sub(r"[^\n]", " ", o.group(0)), sText)


def macro_diagnostics(lFiles, dTexts):
    """
    Returns (file, offset, name, message) of the macros defined in a file with a module, an interface or a program
    and used in another file of the run: design-wide parameters that belong in a file of their own.
    """
    dDefines = {}
    dUsers = {}
    dUnits = {}
    for sPath, oTree in lFiles:
        lUnits = [o.header.name.valueText for s in DESIGN_UNITS for o in walk(oTree.root, s)]
        if lUnits:
            dUnits[sPath] = sorted(lUnits)[0]
        sText = without_comments(dTexts.get(sPath, ""))
        for oMatch in reDefine.finditer(sText):
            dDefines.setdefault(oMatch.group(1), (sPath, oMatch.start(1)))
        for oMatch in reMacro.finditer(sText):
            if oMatch.group(1) not in DIRECTIVES:
                dUsers.setdefault(oMatch.group(1), set()).add(sPath)
    lReturn = []
    for sMacro, (sPath, iOffset) in sorted(dDefines.items()):
        lOthers = sorted(os.path.basename(s) for s in dUsers.get(sMacro, set()) if s != sPath)
        if sPath not in dUnits or not lOthers:
            continue
        sOthers = ", ".join(lOthers[:3]) + (", ..." if len(lOthers) > 3 else "")
        sMessage = f"Macro {sMacro} is used in {sOthers} but defined in the file of {dUnits[sPath]}: define it in a file of global parameters"
        lReturn.append((sPath, iOffset, diagnostics.GLOBAL_MACRO, sMessage))
    return lReturn
