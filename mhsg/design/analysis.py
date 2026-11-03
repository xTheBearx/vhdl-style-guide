# -*- coding: utf-8 -*-
"""
Runs design analysis: GHDL and Yosys on the design described in the configuration, then the design rules on the result.
Findings are reported per VHDL file in the same formats as the other checks.
"""

import contextlib
import json
import tempfile

from mhsg import report, rule_list, rule_set, severity, vhdlFile
from mhsg.design import (
    black_box,
    cdc,
    flat,
    graph,
    netlist,
    project,
    runner,
    tools,
    top,
)
from mhsg.lint import model


class Context:
    """What the design rules see: the design, the result of the tools, the netlist, and the VHDL files when needed."""

    def __init__(self, oDesign, oResult, oNetlist):
        self.design = oDesign
        self.result = oResult
        self.netlist = oNetlist
        self._dFiles = {}
        self._oGraph = None

    def cdc(self):
        """Returns the clock domain crossing Analysis of the flat netlist, built once, or None without a netlist."""
        if getattr(self, "_oCdc", None) is None and self.netlist is not None:
            oFlat = flat.FlatDesign(self.netlist)
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
            self._oGraph = graph.DesignGraph(self.netlist)
        return self._oGraph

    def vhdl_file(self, sFileName):
        """Returns the parsed VHDL file, or None if it cannot be read or parsed."""
        if sFileName not in self._dFiles:
            try:
                lLines, eError = vhdlFile.utils.read_vhdlfile(sFileName)
                self._dFiles[sFileName] = None if eError else vhdlFile.vhdlFile(lLines)
            except Exception:  # pylint: disable=broad-except
                self._dFiles[sFileName] = None
        return self._dFiles[sFileName]

    def refine(self, oLocation, sSignal, bLast=False):
        """
        Returns (file, line) for a cell: the line of the first assignment to the signal in the process that holds
        the location, or the last one with bLast, which is more precise than the process or if statement GHDL points
        at, or the location itself.
        """
        if oLocation is None:
            return None, 0
        oFile = self.vhdl_file(oLocation.file) if sSignal else None
        if oFile is not None:
            # Names carry generate labels before the signal, such as gen_fifo.memory, and record fields after it,
            # such as ctrl_o.cpu_priv: try the parts from the last
            lParts = list(reversed(sSignal.lower().split("[")[0].split(".")))
            for oArchitecture in oFile.get_lint_model().architectures:
                for oProcess in oArchitecture.processes:
                    if not oProcess.line <= oLocation.line <= oProcess.end_line:
                        continue
                    lAssignments = list(model.assignments(oProcess.statements))
                    if bLast:
                        lAssignments.reverse()
                    for sBase in lParts:
                        for oAssignment in lAssignments:
                            if oAssignment.base == sBase:
                                return oLocation.file, oAssignment.line
        return oLocation.file, oLocation.line


def design_rules(oConfig, lLocalRules):
    """Returns the configured rule list with the design rules enabled, and the design rules."""
    oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), oConfig.severity_list, lLocalRules)
    lDesignRules = [o for o in oRules.rules if getattr(o, "design", False)]
    for oRule in lDesignRules:
        oRule.disable = False
    rule_set.apply(oRules, oConfig)
    oRules.configure(oConfig)
    return oRules, [o for o in lDesignRules if not o.disable]


def run(commandLineArguments, oConfig):
    """Runs design analysis and prints its report. Returns the exit status: 1 for errors, else 0."""
    oDesign = project.from_configuration(oConfig.dConfig)
    oTools = tools.find()
    _, lRules = design_rules(oConfig, commandLineArguments.local_rules)
    if oDesign.work_directory:
        oWorkDirectory = contextlib.nullcontext(oDesign.work_directory)
    else:
        oWorkDirectory = tempfile.TemporaryDirectory(prefix="mhsg_design_")
    with oWorkDirectory as sWorkDirectory:
        oResult = configuration_result(oDesign)
        if oResult is None:
            oResult = runner.run(oDesign, oTools, sWorkDirectory)
        oNetlist = None
        if oResult.netlist is not None:
            oNetlist = netlist.Netlist(oResult.netlist, netlist.read_locations(oResult.verilog_file))
        oContext = Context(oDesign, oResult, oNetlist)
        lFindings = [(oRule, oFinding) for oRule in lRules for oFinding in oRule.check_design(oContext)]
        write_cdc_report(getattr(commandLineArguments, "cdc_report", None), oContext)
        write_black_box_template(getattr(commandLineArguments, "black_box_template", None), oContext)
    return print_report(oDesign, oResult, lFindings, oConfig, commandLineArguments.output_format, len(lRules))


def write_cdc_report(sFileName, oContext):
    """Writes the clock domain crossing report, as JSON for a .json file name and as text otherwise."""
    if not sFileName:
        return
    oAnalysis = oContext.cdc()
    if oAnalysis is None:
        dReport = {"top": oContext.design.top, "error": "the design did not synthesize, see design_001"}
        sText = f"Clock domain crossing report for {oContext.design.top}\n\nNot available: the design did not synthesize, see design_001\n"
    else:
        dReport = oAnalysis.report()
        sText = cdc.report_text(dReport)
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


def print_report(oDesign, oResult, lFindings, oConfig, sOutputFormat, iRules):
    dByFile = {}
    for oRule, oFinding in lFindings:
        dByFile.setdefault(oFinding.file or oDesign.top, []).append((oRule, oFinding))
    bErrors = oResult.failed_stage is not None
    for sFile in sorted(dByFile):
        dRunInfo = run_info(sFile, dByFile[sFile], oConfig.severity_list, iRules)
        bErrors = bErrors or any(d["severity"]["type"] == severity.error_type for d in dRunInfo["violations"])
        sOutputStd, sOutputErr = format_report(dRunInfo, sOutputFormat)
        if sOutputStd:
            print(sOutputStd, end="" if sOutputStd.endswith("\n") else "\n")
        if sOutputErr:
            print(sOutputErr)
    if not dByFile and sOutputFormat != "syntastic":
        print(f"Design analysis of {oDesign.top}: no findings ({iRules} design rules checked)")
    return 1 if bErrors else 0


def run_info(sFile, lFindings, oSeverityList, iRules):
    lViolations = []
    for oRule, oFinding in sorted(lFindings, key=lambda t: t[1].line):
        oSeverity = oRule.get_report_severity()
        lViolations.append(
            {
                "severity": {"name": oSeverity.name, "type": oSeverity.type},
                "rule": oRule.get_display_id(),
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
