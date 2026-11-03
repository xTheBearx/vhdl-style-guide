# -*- coding: utf-8 -*-
"""
Runs design analysis: GHDL and Yosys on the design described in the configuration, then the design rules on the result.
Findings are reported per VHDL file in the same formats as the other checks.
"""

import tempfile

from mhsg import report, rule_list, rule_set, severity, vhdlFile
from mhsg.design import netlist, project, runner, tools
from mhsg.lint import model


class Context:
    """What the design rules see: the design, the result of the tools, the netlist, and the VHDL files when needed."""

    def __init__(self, oDesign, oResult, oNetlist):
        self.design = oDesign
        self.result = oResult
        self.netlist = oNetlist
        self._dFiles = {}

    def vhdl_file(self, sFileName):
        """Returns the parsed VHDL file, or None if it cannot be read or parsed."""
        if sFileName not in self._dFiles:
            try:
                lLines, eError = vhdlFile.utils.read_vhdlfile(sFileName)
                self._dFiles[sFileName] = None if eError else vhdlFile.vhdlFile(lLines)
            except Exception:  # pylint: disable=broad-except
                self._dFiles[sFileName] = None
        return self._dFiles[sFileName]

    def refine(self, oLocation, sSignal):
        """
        Returns (file, line) for a cell: the line of the first assignment to the signal in the process that holds
        the location, which is more precise than the process or if statement GHDL points at, or the location itself.
        """
        if oLocation is None:
            return None, 0
        oFile = self.vhdl_file(oLocation.file) if sSignal else None
        if oFile is not None:
            sBase = sSignal.lower().split("[")[0]
            for oArchitecture in oFile.get_lint_model().architectures:
                for oProcess in oArchitecture.processes:
                    if not oProcess.line <= oLocation.line <= oProcess.end_line:
                        continue
                    for oAssignment in model.assignments(oProcess.statements):
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
    with tempfile.TemporaryDirectory(prefix="mhsg_design_") as sWorkDirectory:
        oResult = runner.run(oDesign, oTools, sWorkDirectory)
        oNetlist = None
        if oResult.netlist is not None:
            oNetlist = netlist.Netlist(oResult.netlist, netlist.read_locations(oResult.verilog_file))
        oContext = Context(oDesign, oResult, oNetlist)
        lFindings = [(oRule, oFinding) for oRule in lRules for oFinding in oRule.check_design(oContext)]
    return print_report(oDesign, oResult, lFindings, oConfig, commandLineArguments.output_format, len(lRules))


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
