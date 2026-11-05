# -*- coding: utf-8 -*-
"""
Tool qualification: runs the examples of the checks of a rule set and compares what MHSG finds with the results
recorded for them, for the evidence a DO-254 or DO-330 tool qualification asks for.

The examples and their expected results are in mhsg/qualification: a manifest for each built in rule set, named
after it, lists for each rule of the set the example files it runs on, with the findings expected of that rule in each,
and for the rules of design analysis the designs. scripts/make_qualification_suite.py makes the manifests from the
test inputs of MHSG; the expected results it records must be reviewed before they are committed.

    mhsg --qualify do254 --qualify_report qualification.json

runs every example of the set, each on its own as MHSG would check a file in lint mode with the set, and writes a
report of each case: the expected and actual findings, and whether they match. A rule of design analysis needs GHDL
and Yosys; without them its cases are not run, and the report says so. The exit status is 1 if a case does not match.
"""

import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile

from mhsg import provenance, rule_set, yaml_files
from mhsg.rules.sv_lint import verilator_rule
from mhsg.svFile import verilator

DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qualification")
PASS = "pass"
FAIL = "fail"
NOT_RUN = "not run"


def manifest_file(sRuleSet):
    return os.path.join(DIRECTORY, sRuleSet.lower() + ".yaml")


def load(sRuleSet):
    """Returns the manifest of a built in rule set, or raises a ValueError if it has none."""
    sFile = manifest_file(sRuleSet)
    if not os.path.isfile(sFile):
        lSets = sorted(os.path.splitext(s)[0] for s in os.listdir(DIRECTORY) if s.endswith(".yaml"))
        raise ValueError(f"ERROR: no qualification suite for rule set {sRuleSet}; there are suites for {', '.join(lSets)}")
    with open(sFile, encoding="utf-8") as oFile:
        return yaml_files.safe_load(oFile)


def mhsg_command():
    """The command that runs this MHSG in a process of its own."""
    return [sys.executable, "-c", "from mhsg.__main__ import main; main()"]


def run_file(sRuleSet, sFile):
    """Runs MHSG in lint mode with a rule set on one file and returns its findings as {rule: [[line, message], ...]}."""
    with tempfile.TemporaryDirectory(prefix="mhsg_qualify_") as sDirectory:
        sJson = os.path.join(sDirectory, "findings.json")
        lCommand = mhsg_command() + ["-f", sFile, "--lint_only", "--rule_set", sRuleSet, "-ap", "-of", "syntastic", "-js", sJson]
        subprocess.run(lCommand, capture_output=True, text=True, check=False, cwd=sDirectory)
        try:
            with open(sJson, encoding="utf-8") as oFile:
                dJson = json.load(oFile)
        except (OSError, ValueError):
            return None
    dReturn = {}
    for dFile in dJson.get("files", []):
        for dViolation in dFile.get("violations", []):
            dReturn.setdefault(dViolation["rule"], []).append([int(dViolation["linenumber"]), dViolation["solution"]])
    return dReturn


def run_design(sRuleSet, dDesign):
    """Runs design analysis with a rule set and returns its findings as {rule: [[file, line, message], ...]}, or None."""
    with tempfile.TemporaryDirectory(prefix="mhsg_qualify_") as sDirectory:
        dDesign = dict(dDesign)
        dDesign["libraries"] = [{"name": d["name"], "files": [os.path.join(DIRECTORY, s) for s in d["files"]]} for d in dDesign.get("libraries", [])]
        sConfiguration = os.path.join(sDirectory, "design.json")
        with open(sConfiguration, "w", encoding="utf-8") as oFile:
            json.dump({"design": dDesign}, oFile)
        sJson = os.path.join(sDirectory, "findings.json")
        lCommand = mhsg_command() + ["--design", "-c", sConfiguration, "--rule_set", sRuleSet, "-of", "syntastic", "--json", sJson]
        subprocess.run(lCommand, capture_output=True, text=True, check=False, cwd=sDirectory)
        try:
            with open(sJson, encoding="utf-8") as oFile:
                dJson = json.load(oFile)
        except (OSError, ValueError):
            return None
    dReturn = {}
    for dFile in dJson.get("files", []):
        sFile = os.path.relpath(dFile["file_path"], DIRECTORY) if os.path.isabs(dFile["file_path"]) else dFile["file_path"]
        for dViolation in dFile.get("violations", []):
            dReturn.setdefault(dViolation["rule"], []).append([sFile, int(dViolation["linenumber"]), dViolation["solution"]])
    return dReturn


def design_tools():
    """Returns None if GHDL and Yosys can run, else why not."""
    from mhsg import exceptions  # pylint: disable=import-outside-toplevel
    from mhsg.design import tools  # pylint: disable=import-outside-toplevel

    try:
        tools.find()
    except exceptions.DesignError as e:
        return e.message
    return None


def run(sRuleSet, iJobs=4):
    """Runs the qualification suite of a rule set and returns the report as a dictionary."""
    dManifest = load(sRuleSet)
    oRuleSet = rule_set.load(sRuleSet)
    dLabels = {}
    for oSet in oRuleSet.all_sets():
        for oCheck in oSet.checks:
            for sRule in oCheck.rules:
                dLabels.setdefault(sRule, []).append(oSet.label(oCheck))
    lCases = dManifest.get("cases", [])
    lFiles = sorted({d["file"] for d in lCases})
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, iJobs)) as oPool:
        dResults = dict(zip(lFiles, oPool.map(lambda s: run_file(sRuleSet, os.path.join(DIRECTORY, s)), lFiles)))
    lReport = []
    bVerilator = verilator.find({}) is not None
    for dCase in lCases:
        dActual = dResults.get(dCase["file"])
        dEntry = {"rule": dCase["rule"], "checks": dLabels.get(dCase["rule"], []), "file": dCase["file"], "expected": dCase["expected"]}
        if dCase["rule"] in verilator_rule.RULES and not bVerilator:
            dEntry.update({"actual": None, "result": NOT_RUN, "reason": "the rule reports Verilator's warnings, and Verilator is not installed"})
        elif dActual is None:
            dEntry.update({"actual": None, "result": FAIL, "reason": "MHSG did not run on the file"})
        else:
            dEntry["actual"] = dActual.get(dCase["rule"], [])
            dEntry["result"] = PASS if sorted(dEntry["actual"]) == sorted(dCase["expected"]) else FAIL
        lReport.append(dEntry)
    sNoTools = design_tools() if dManifest.get("design_cases") else None
    # Each design runs once, for all the rules that have cases on it
    dDesigns = {}
    for dCase in dManifest.get("design_cases", []) if not sNoTools else []:
        dDesigns.setdefault(json.dumps(dCase["design"], sort_keys=True), dCase["design"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, iJobs)) as oPool:
        dDesignResults = dict(zip(dDesigns, oPool.map(lambda d: run_design(sRuleSet, d), dDesigns.values())))
    for dCase in dManifest.get("design_cases", []):
        dEntry = {"rule": dCase["rule"], "checks": dLabels.get(dCase["rule"], []), "design": dCase["name"], "expected": dCase["expected"]}
        if sNoTools:
            dEntry.update({"actual": None, "result": NOT_RUN, "reason": sNoTools})
        else:
            dActual = dDesignResults.get(json.dumps(dCase["design"], sort_keys=True))
            if dActual is None:
                dEntry.update({"actual": None, "result": FAIL, "reason": "design analysis did not run"})
            else:
                dEntry["actual"] = dActual.get(dCase["rule"], [])
                dEntry["result"] = PASS if sorted(dEntry["actual"]) == sorted(dCase["expected"]) else FAIL
        lReport.append(dEntry)
    dSummary = {PASS: 0, FAIL: 0, NOT_RUN: 0}
    for dEntry in lReport:
        dSummary[dEntry["result"]] += 1
    setCovered = {d["rule"] for d in lReport}
    lUncovered = sorted(s for s in dLabels if s not in setCovered)
    return {
        "rule_set": {"name": oRuleSet.name, "version": oRuleSet.version, "sha256": provenance.file_digest(oRuleSet.filename)},
        "suite": {"file": os.path.basename(manifest_file(sRuleSet)), "sha256": provenance.file_digest(manifest_file(sRuleSet))},
        "summary": dSummary,
        "rules_without_cases": lUncovered,
        "cases": lReport,
    }


def text(dReport, dRecord):
    """Returns the report as text."""
    lLines = [f"Qualification of rule set {dReport['rule_set']['name']} version {dReport['rule_set']['version']}", ""]
    for dEntry in dReport["cases"]:
        sWhere = dEntry.get("file") or dEntry.get("design")
        sChecks = ", ".join(dEntry["checks"])
        lLines.append(f"{dEntry['result'].upper():8} {dEntry['rule']} ({sChecks}) on {sWhere}")
        if dEntry["result"] != PASS:
            if dEntry.get("reason"):
                lLines.append(f"         {dEntry['reason']}")
            else:
                lLines.append(f"         expected {len(dEntry['expected'])}: {dEntry['expected']}")
                lLines.append(f"         actual   {len(dEntry['actual'])}: {dEntry['actual']}")
    dSummary = dReport["summary"]
    lLines += ["", f"Summary: {dSummary[PASS]} passed, {dSummary[FAIL]} failed, {dSummary[NOT_RUN]} not run"]
    if dReport["rules_without_cases"]:
        lLines.append("Rules of the set without examples: " + ", ".join(dReport["rules_without_cases"]))
    lLines += ["", "Run"] + [f"  {s}" for s in provenance.summary(dRecord)]
    return "\n".join(lLines) + "\n"


def main(commandLineArguments, oConfig):
    """Runs --qualify and exits with 0 if every case matches."""
    try:
        dReport = run(commandLineArguments.qualify, commandLineArguments.jobs or 4)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    # The record names the versions of every tool the cases ran: GHDL, Yosys and Verilator as well
    oTools = None
    if design_tools() is None:
        from mhsg.design import tools  # pylint: disable=import-outside-toplevel

        oTools = tools.find()
    dRecord = provenance.record(commandLineArguments, oConfig, oTools)
    sVerilator = verilator.find({})
    dRecord["verilator"] = verilator.version(sVerilator) if sVerilator else None
    dReport["run"] = dRecord
    sFile = getattr(commandLineArguments, "qualify_report", None)
    if sFile:
        with open(sFile, "w", encoding="utf-8") as oFile:
            if sFile.lower().endswith(".json"):
                json.dump(dReport, oFile, indent=2)
                oFile.write("\n")
            else:
                oFile.write(text(dReport, dRecord))
    print(text(dReport, dRecord), end="")
    sys.exit(1 if dReport["summary"][FAIL] else 0)
