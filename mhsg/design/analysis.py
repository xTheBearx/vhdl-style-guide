# -*- coding: utf-8 -*-
"""
Runs design analysis: GHDL and Yosys on the design described in the configuration, then the design rules on the result.
Findings are reported per VHDL file in the same formats as the other checks.
"""

import contextlib
import importlib
import json
import sys
import tempfile

from mhsg import (
    language,
    provenance,
    report,
    rule_list,
    rule_set,
    severity,
    vhdlFile,
    waivers,
)
from mhsg.design import (
    black_box,
    cdc,
    flat,
    graph,
    netlist,
    project,
    runner,
    source_summary,
    tools,
    top,
)
from mhsg.rules import sv_tree

# mhsg.svFile exports the class svFile under the name of its module
svFile = importlib.import_module("mhsg.svFile.svFile")


class Context:
    """What the design rules see: the design, the result of the tools, the netlist, and the VHDL files when needed."""

    def __init__(self, oDesign, oResult, oNetlist, oTools=None):
        self.design = oDesign
        self.result = oResult
        self.netlist = oNetlist
        # The tools, for rules that run them again, such as design_019
        self.tools = oTools
        self._dFiles = {}
        self._oGraph = None

    def flat(self):
        """Returns the flat netlist, built once, or None without a netlist."""
        if getattr(self, "_oFlat", None) is None and self.netlist is not None:
            self._oFlat = flat.FlatDesign(self.netlist)
        return getattr(self, "_oFlat", None)

    def box_paths(self, sModule, sCell):
        """The flat names of the instances of a black box cell of a module, such as u_top.u_box."""
        if getattr(self, "_dBoxPaths", None) is None:
            self._dBoxPaths = {}
            oFlat = self.flat()
            for oCell in oFlat.cells if oFlat is not None else []:
                if oCell.is_black_box():
                    self._dBoxPaths.setdefault((oCell.module, oCell.name), []).append(repr(oCell))
        return self._dBoxPaths.get((sModule, sCell), [])

    def cdc(self):
        """Returns the clock domain crossing Analysis of the flat netlist, built once, or None without a netlist."""
        if getattr(self, "_oCdc", None) is None and self.netlist is not None:
            oFlat = self.flat()
            dConstraints = self.design.cdc if self.design is not None else {}
            oBlackBoxes = self.design.black_boxes if self.design is not None else None
            self._oCdc = cdc.Analysis(oFlat, dConstraints, self.locate_cell, oBlackBoxes)
        return getattr(self, "_oCdc", None)

    def locate_cell(self, oCell, sSignal=None):
        """Returns (file, line) of a flat cell, refined to the assignment of the signal."""
        oLocation = self.netlist.location(oCell.module, oCell.name)
        return self.refine(oLocation, sSignal) if oLocation is not None else (None, 0)

    def graph(self):
        """Returns the DesignGraph of the netlist, built once for all rules, or None without a netlist."""
        if self._oGraph is None and self.netlist is not None:
            oBlackBoxes = self.design.black_boxes if self.design is not None else None
            self._oGraph = graph.DesignGraph(self.netlist, oBlackBoxes, self.box_paths)
        return self._oGraph

    def instance_graph(self):
        """
        Returns the DesignGraph in which the modules whose black boxes have declarations of single instances that differ
        between their instances have a copy for each instance, see graph.instance_copies; the DesignGraph when none do.
        """
        if getattr(self, "_oInstanceGraph", None) is None and self.netlist is not None:
            oBlackBoxes = self.design.black_boxes if self.design is not None else None
            tCopies = graph.instance_copies(self.netlist, oBlackBoxes, self.box_paths)
            self._oInstanceGraph = graph.DesignGraph(tCopies[0], oBlackBoxes, tCopies[1]) if tCopies is not None else self.graph()
        return getattr(self, "_oInstanceGraph", None)

    def vhdl_summary(self, sFileName):
        """
        Returns the processes of a VHDL file by architecture, see source_summary.py, or None if it cannot be read or
        parsed, or is not a VHDL file.
        """
        if language.of_file(sFileName) != language.VHDL:
            return None
        if sFileName not in self._dFiles:
            self._dFiles[sFileName] = source_summary.load(sFileName)
        return self._dFiles[sFileName]

    def sv_file(self, sFileName):
        """The parsed SystemVerilog file, or None if it cannot be read."""
        dFiles = self.__dict__.setdefault("_dSvFiles", {})
        if sFileName not in dFiles:
            try:
                lLines, eError = vhdlFile.utils.read_vhdlfile(sFileName)
                dFiles[sFileName] = None if eError else svFile.svFile(lLines, sFilename=sFileName)
            except Exception:  # pylint: disable=broad-except
                dFiles[sFileName] = None
        return dFiles[sFileName]

    def refine_verilog(self, oLocation, lParts, bLast):
        """
        Returns the line of the first assignment, or the last with bLast, to a signal in the always block or
        continuous assignment at a location of Yosys, which is the start of the block, or None.
        """
        oFile = self.sv_file(oLocation.file)
        if oFile is None:
            return None
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            oFirst, oLast = oBlock.getFirstToken(), oBlock.getLastToken()
            if oFirst is None or not oFile.line_of(oFirst.location.offset) <= oLocation.line <= oFile.line_of(oLast.location.offset):
                continue
            lLines = []
            for oNode in sv_tree.descendants(oBlock):
                if oNode.kind.name in ("AssignmentExpression", "NonblockingAssignmentExpression"):
                    oTarget = oNode.left.getFirstToken()
                    if oTarget is not None and oTarget.rawText.lower() in lParts:
                        lLines.append(oFile.line_of(oTarget.location.offset))
            if lLines:
                return max(lLines) if bLast else min(lLines)
        return None

    def refine(self, oLocation, sSignal, bLast=False):
        """
        Returns (file, line) for a cell: the line of the first assignment to the signal in the process that holds
        the location, or the last one with bLast, which is more precise than the process or if statement GHDL points
        at, or the location itself.
        """
        if oLocation is None:
            return None, 0
        # Only VHDL files are refined to the assignment; Yosys locates the cells of Verilog at the assignment itself
        if sSignal and language.of_file(oLocation.file) == language.SYSTEMVERILOG:
            iLine = self.refine_verilog(oLocation, list(reversed(sSignal.lower().split("[")[0].split("."))), bLast)
            return oLocation.file, iLine if iLine is not None else oLocation.line
        lArchitectures = self.vhdl_summary(oLocation.file) if sSignal and language.of_file(oLocation.file) == language.VHDL else None
        if lArchitectures is not None:
            # Names carry generate labels before the signal, such as gen_fifo.memory, and record fields after it,
            # such as ctrl_o.cpu_priv: try the parts from the last
            lParts = list(reversed(sSignal.lower().split("[")[0].split(".")))
            for oArchitecture in lArchitectures:
                for oProcess in oArchitecture.processes:
                    if oProcess.line <= oLocation.line <= oProcess.end_line:
                        iLine = assignment_line(oProcess, lParts, bLast)
                        if iLine is not None:
                            return oLocation.file, iLine
            # Later versions of GHDL locate some cells, such as latches, at the declaration of the signal or port they
            # drive instead of the process: use the first process that assigns the signal in the architecture whose
            # statements follow the declaration, the one it belongs to when a file holds several
            lFollowing = [o for o in lArchitectures if o.first_statement is not None and declaration_line(o, oLocation.line)]
            if lFollowing or all(declaration_line(o, oLocation.line) for o in lArchitectures):
                lSearched = [min(lFollowing, key=lambda o: o.first_statement)] if lFollowing else lArchitectures
                for oArchitecture in lSearched:
                    for oProcess in oArchitecture.processes:
                        iLine = assignment_line(oProcess, lParts, bLast)
                        if iLine is not None:
                            return oLocation.file, iLine
        return oLocation.file, oLocation.line


def assignment_line(oProcess, lParts, bLast=False):
    """Returns the line of the first assignment in a process to one of the names, tried in order, or of the last with bLast."""
    lAssignments = list(oProcess.assignments)
    if bLast:
        lAssignments.reverse()
    for sBase in lParts:
        for sName, iLine in lAssignments:
            if sName == sBase:
                return iLine
    return None


def declaration_line(oArchitecture, iLine):
    """Returns whether a line comes before the statements of an architecture: in its declarations, or before it."""
    return oArchitecture.first_statement is None or iLine < oArchitecture.first_statement


def design_rules(oConfig, lLocalRules):
    """Returns the configured rule list with the design rules enabled, and the design rules."""
    oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), oConfig.severity_list, lLocalRules)
    lDesignRules = [o for o in oRules.rules if getattr(o, "design", False)]
    for oRule in lDesignRules:
        oRule.disable = oRule.disabled_in_design
    rule_set.apply(oRules, oConfig)
    oRules.configure(oConfig)
    return oRules, [o for o in lDesignRules if not o.disable]


def run(commandLineArguments, oConfig):
    """Runs design analysis and prints its report. Returns the exit status: 1 for errors, else 0."""
    oDesign = project.from_configuration(oConfig.dConfig)
    oTools = tools.find(bGhdl=oDesign.language != "systemverilog")
    dRecord = provenance.record(commandLineArguments, oConfig, oTools)
    _, lRules = design_rules(oConfig, commandLineArguments.local_rules)
    if oDesign.work_directory:
        oWorkDirectory = contextlib.nullcontext(oDesign.work_directory)
    else:
        oWorkDirectory = tempfile.TemporaryDirectory(prefix="mhsg_design_")
    with oWorkDirectory as sWorkDirectory:
        # The generics of a VHDL top are checked before GHDL runs; Yosys checks the parameters of a Verilog top
        oResult = configuration_result(oDesign) if oDesign.language != "systemverilog" else None
        if oResult is None:
            oResult = runner.run(oDesign, oTools, sWorkDirectory)
        oNetlist = None
        if oResult.netlist is not None:
            lFiles = [s for o in oDesign.libraries for s in o.files]
            # Locations come from GHDL's Verilog for VHDL, and from the src attributes of the netlist for Verilog
            dLocations = netlist.read_locations(oResult.verilog_file, lFiles) if oResult.verilog_file else {}
            oNetlist = netlist.Netlist(oResult.netlist, dLocations, lFiles)
        oContext = Context(oDesign, oResult, oNetlist, oTools)
        lFindings = [(oRule, oFinding) for oRule in lRules for oFinding in oRule.check_design(oContext)]
        write_cdc_report(getattr(commandLineArguments, "cdc_report", None), oContext, dRecord)
        write_black_box_template(getattr(commandLineArguments, "black_box_template", None), oContext)
    lWaivers = getattr(oConfig, "waivers", None) or []
    lFindings, lWaived = apply_waivers(oDesign, lRules, lFindings, lWaivers)
    iStatus, lRunInfo = print_report(oDesign, oResult, lFindings, oConfig, commandLineArguments.output_format, len(lRules), lWaived)
    if getattr(commandLineArguments, "json", None):
        with open(commandLineArguments.json, "w", encoding="utf-8") as oFile:
            # The entries of the files have the keys of those --json writes for the files of a run
            lFiles = [
                {
                    "file_path": d["filename"],
                    "violations": [
                        {
                            "rule": v["rule_id"],
                            **({"checks": v["checks"]} if v["checks"] else {}),
                            "linenumber": int(v["lineNumber"]),
                            "severity": v["severity"]["name"],
                            "solution": v["solution"],
                        }
                        for v in d["violations"]
                    ],
                    **({"waived": d["waived"]} if d["waived"] else {}),
                }
                for d in lRunInfo
            ]
            json.dump({"files": lFiles, "run": dRecord}, oFile, indent=2)
            oFile.write("\n")
    return iStatus


def write_cdc_report(sFileName, oContext, dRecord=None):
    """
    Writes the clock domain crossing report, as JSON for a .json file name and as text otherwise, with the record of
    the run: the versions of the tools and the configuration.
    """
    if not sFileName:
        return
    oAnalysis = oContext.cdc()
    if oAnalysis is None:
        dReport = {"top": oContext.design.top, "error": "the design did not synthesize, see design_001"}
        sText = f"Clock domain crossing report for {oContext.design.top}\n\nNot available: the design did not synthesize, see design_001\n"
    else:
        dReport = oAnalysis.report()
        sText = cdc.report_text(dReport)
    if dRecord is not None:
        dReport = {**dReport, "run": dRecord}
        sText = sText.rstrip("\n") + "\n\nRun\n" + "".join(f"  {s}\n" for s in provenance.summary(dRecord))
    with open(sFileName, "w", encoding="utf-8") as oFile:
        if sFileName.lower().endswith(".json"):
            json.dump(dReport, oFile, indent=2)
            oFile.write("\n")
        else:
            oFile.write(sText)


def write_black_box_template(sFileName, oContext):
    """Writes a YAML template of declarations for the black boxes of the design that have none."""
    if not sFileName:
        return
    oAnalysis = oContext.cdc()
    with open(sFileName, "w", encoding="utf-8") as oFile:
        if oAnalysis is None:
            oFile.write("# The design did not synthesize, see design_001, so its black boxes are not known.\n")
        else:
            oFile.write(black_box.template(oAnalysis.flat, oAnalysis.box_library))


def configuration_result(oDesign):
    """Returns a failed Result for generics of the top entity that need a value, or None if the design can run."""
    lMessages = [
        runner.Message(sFile, iLine, 0, "error", f"generic {sName} of {oDesign.top} has no default value; set it under generics", "configuration")
        for sFile, iLine, sName in top.missing_generics(oDesign)
    ]
    lMessages += [
        runner.Message(sFile, iLine, 0, "error", f"{oDesign.top} has no generic {sName}, which is set under generics", "configuration")
        for sFile, iLine, sName in top.unknown_generics(oDesign)
    ]
    if not lMessages:
        return None
    oResult = runner.Result()
    oResult.failed_stage = "configuration"
    oResult.messages = lMessages
    return oResult


def apply_waivers(oDesign, lRules, lFindings, lWaivers):
    """
    Returns (the findings no waiver matches, the waived ones as (rule, finding, waiver)), and warns of the waivers of
    design rules that matched nothing, see waivers.py.
    """
    if not lWaivers:
        return lFindings, []
    lFiles = [s for o in oDesign.libraries for s in o.files]
    dUse = {}
    for oRule in lRules:
        for oWaiver in lWaivers:
            if oWaiver.applies_to_rule(oRule.get_unique_id()) and (oWaiver.file is None or any(oWaiver.applies_to_file(s) for s in lFiles)):
                dUse.setdefault(oWaiver.index, False)
    lKept = []
    lWaived = []
    for oRule, oFinding in lFindings:
        oWaiver = waivers.first_match(lWaivers, oRule.get_unique_id(), oFinding.file, oFinding.line, oFinding.message)
        if oWaiver is None:
            lKept.append((oRule, oFinding))
        else:
            lWaived.append((oRule, oFinding, oWaiver))
            dUse[oWaiver.index] = True
    for oWaiver in waivers.unused(lWaivers, [dUse]):
        print(f"WARNING: {oWaiver.describe()} matched no finding; it may be out of date", file=sys.stderr)
    return lKept, lWaived


def print_report(oDesign, oResult, lFindings, oConfig, sOutputFormat, iRules, lWaived=()):
    dByFile = {}
    dWaived = {}
    lRunInfo = []
    for oRule, oFinding in lFindings:
        dByFile.setdefault(oFinding.file or oDesign.top, []).append((oRule, oFinding))
    for oRule, oFinding, oWaiver in lWaived:
        dEntry = {"rule": oRule.get_unique_id(), "linenumber": oFinding.line, "severity": oRule.get_report_severity().name, "solution": oFinding.message}
        dEntry.update(oWaiver.entry())
        dWaived.setdefault(oFinding.file or oDesign.top, []).append(dEntry)
        dByFile.setdefault(oFinding.file or oDesign.top, [])
    bErrors = oResult.failed_stage is not None
    for sFile in sorted(dByFile):
        dRunInfo = run_info(sFile, dByFile[sFile], oConfig.severity_list, iRules)
        dRunInfo["waived"] = sorted(dWaived.get(sFile, []), key=lambda d: d["linenumber"])
        lRunInfo.append(dRunInfo)
        bErrors = bErrors or any(d["severity"]["type"] == severity.error_type for d in dRunInfo["violations"])
        sOutputStd, sOutputErr = format_report(dRunInfo, sOutputFormat)
        if sOutputStd:
            print(sOutputStd, end="" if sOutputStd.endswith("\n") else "\n")
        if sOutputErr:
            print(sOutputErr)
    if not any(dByFile.values()) and sOutputFormat != "syntastic":
        sWaived = f", {len(lWaived)} waived" if lWaived else ""
        print(f"Design analysis of {oDesign.top}: no findings ({iRules} design rules checked{sWaived})")
    return (1 if bErrors else 0), lRunInfo


def run_info(sFile, lFindings, oSeverityList, iRules):
    lViolations = []
    for oRule, oFinding in sorted(lFindings, key=lambda t: t[1].line):
        oSeverity = oRule.get_report_severity()
        lViolations.append(
            {
                "severity": {"name": oSeverity.name, "type": oSeverity.type},
                "rule": oRule.get_display_id(),
                "rule_id": oRule.get_unique_id(),
                "checks": list(oRule.rule_set_labels),
                "lineNumber": str(oFinding.line),
                "solution": oFinding.message,
            },
        )
    dSeverities = {o.name: 0 for o in oSeverityList.get_severities()}
    for dViolation in lViolations:
        dSeverities[dViolation["severity"]["name"]] = dSeverities.get(dViolation["severity"]["name"], 0) + 1
    return {
        "filename": sFile,
        "stopPhase": 7,
        "violations": lViolations,
        "num_rules_checked": iRules,
        "total_violations": len(lViolations),
        "maxSeverityNameLength": oSeverityList.iMaxNameLength,
        "severities": dSeverities,
    }


def format_report(dRunInfo, sOutputFormat):
    if sOutputFormat == "mhsg":
        return report.mhsg_stdout.print_output(dRunInfo)
    if sOutputFormat == "syntastic":
        return report.syntastic_stdout.print_output(dRunInfo)
    return report.summary_stdout.print_output(dRunInfo)
