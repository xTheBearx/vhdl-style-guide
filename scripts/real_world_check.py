#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run mhsg over open source VHDL projects and report files it cannot handle.

Each file is checked, fixed, and then fixed again.  The result for a file is
one of:

  OK               every step succeeded and the second fix changed nothing
  CRASH            the check raised an exception
  PARSE_ERROR      the file could not be parsed
  FIX_CRASH        the fix raised an exception
  FIX_BROKE_PARSE  the fixed file could not be parsed
  NOT_IDEMPOTENT   the second fix changed the file again
  TIMEOUT          a step took longer than the time limit

The projects, the commits they are pinned to, and the known issues are listed
in scripts/real_world_projects.yaml.  The run fails when a file has a status
other than OK that is not listed as a known issue.

Example:

  python scripts/real_world_check.py --jobs 4 --project osvvm
"""

import argparse
import concurrent.futures
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MHSG = os.path.join(REPO_ROOT, "bin", "mhsg")
DEFAULT_PROJECTS = os.path.join(REPO_ROOT, "scripts", "real_world_projects.yaml")
DEFAULT_CACHE = os.path.join(REPO_ROOT, ".real_world_cache")
EXTENSIONS = (".vhd", ".vhdl")

OK = "OK"
CRASH = "CRASH"
PARSE_ERROR = "PARSE_ERROR"
FIX_CRASH = "FIX_CRASH"
FIX_BROKE_PARSE = "FIX_BROKE_PARSE"
NOT_IDEMPOTENT = "NOT_IDEMPOTENT"
TIMEOUT = "TIMEOUT"
STATUSES = (OK, CRASH, PARSE_ERROR, FIX_CRASH, FIX_BROKE_PARSE, NOT_IDEMPOTENT, TIMEOUT)


def output_problem(sOutput):
    """Returns "crash", "parse" or None for the output of an mhsg run."""
    if "Traceback (most recent call last)" in sOutput:
        return "crash"
    if "Error while processing" in sOutput:
        return "parse"
    return None


def classify(sCheckOutput, sFixOutput=None, sSecondFixOutput=None, sFirstFix=None, sSecondFix=None):
    """
    Returns the status of a file from the output of its three mhsg runs and
    the file contents after each fix.  Arguments for steps that did not run
    are None.
    """
    sProblem = output_problem(sCheckOutput)
    if sProblem == "crash":
        return CRASH, sCheckOutput
    if sProblem == "parse":
        return PARSE_ERROR, sCheckOutput

    sProblem = output_problem(sFixOutput or "")
    if sProblem == "crash":
        return FIX_CRASH, sFixOutput
    if sProblem == "parse":
        # The check parsed the file, so the parse error came from a fix
        # applied during this run.
        return FIX_BROKE_PARSE, sFixOutput

    sProblem = output_problem(sSecondFixOutput or "")
    if sProblem == "parse":
        return FIX_BROKE_PARSE, sSecondFixOutput
    if sProblem == "crash":
        return FIX_CRASH, sSecondFixOutput

    if sFirstFix != sSecondFix:
        lDiff = difflib.unified_diff(
            (sFirstFix or "").splitlines(),
            (sSecondFix or "").splitlines(),
            "first fix",
            "second fix",
            lineterm="",
        )
        return NOT_IDEMPOTENT, "\n".join(lDiff)

    return OK, ""


def run_mhsg(lArguments, iTimeout):
    """Runs mhsg and returns its combined output."""
    oResult = subprocess.run(
        [sys.executable, MHSG] + lArguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=iTimeout,
        check=False,
    )
    return oResult.stdout


def read(sFileName):
    with open(sFileName, encoding="utf-8", errors="surrogateescape") as oFile:
        return oFile.read()


def check_file(sSource, sWorkDir, iTimeout):
    """Checks one file and returns (status, details)."""
    sCopy = os.path.join(sWorkDir, os.path.basename(sSource))
    shutil.copyfile(sSource, sCopy)
    try:
        sCheck = run_mhsg(["-f", sCopy, "-of", "syntastic"], iTimeout)
        if output_problem(sCheck):
            return classify(sCheck)
        sFix = run_mhsg(["-f", sCopy, "--fix", "-of", "syntastic"], iTimeout)
        if output_problem(sFix):
            return classify(sCheck, sFix)
        sFirstFix = read(sCopy)
        sSecondFixOutput = run_mhsg(["-f", sCopy, "--fix", "-of", "syntastic"], iTimeout)
        return classify(sCheck, sFix, sSecondFixOutput, sFirstFix, read(sCopy))
    except subprocess.TimeoutExpired:
        return TIMEOUT, f"A step took longer than {iTimeout} seconds"


def check_file_isolated(sSource, iTimeout):
    with tempfile.TemporaryDirectory(prefix="mhsg_rw_") as sWorkDir:
        return check_file(sSource, sWorkDir, iTimeout)


def git(lArguments, sDirectory):
    subprocess.run(["git"] + lArguments, cwd=sDirectory, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def fetch_project(dProject, sCache):
    """Makes sure the pinned commit of a project is checked out in the cache."""
    sDirectory = os.path.join(sCache, dProject["name"])
    if os.path.isdir(os.path.join(sDirectory, ".git")):
        sHead = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=sDirectory,
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        ).stdout.strip()
        if sHead == dProject["commit"]:
            return sDirectory
    else:
        os.makedirs(sDirectory, exist_ok=True)
        git(["init", "-q"], sDirectory)
        git(["remote", "add", "origin", dProject["url"]], sDirectory)
    git(["fetch", "-q", "--depth", "1", "origin", dProject["commit"]], sDirectory)
    git(["checkout", "-q", "--force", "FETCH_HEAD"], sDirectory)
    return sDirectory


def relative_path(sFileName, sDirectory):
    return os.path.relpath(sFileName, sDirectory).replace(os.sep, "/")


def find_vhdl_files(sDirectory, lExclude=()):
    """Returns the VHDL files below a directory, except the excluded paths."""
    lFiles = []
    for sRoot, lDirectories, lFileNames in os.walk(sDirectory):
        lDirectories[:] = sorted(s for s in lDirectories if s != ".git")
        for sFileName in sorted(lFileNames):
            sPath = os.path.join(sRoot, sFileName)
            if sFileName.lower().endswith(EXTENSIONS) and relative_path(sPath, sDirectory) not in lExclude:
                lFiles.append(sPath)
    return lFiles


def compare_with_known(lResults, dKnown):
    """
    Splits the results of a project into new failures, known failures, and
    known issues that no longer occur.  lResults holds dictionaries with
    "file" and "status" keys.
    """
    lNew = []
    lKnown = []
    lResolved = []
    for dResult in lResults:
        sExpected = dKnown.get(dResult["file"], OK)
        if dResult["status"] == OK:
            if sExpected != OK:
                lResolved.append(dResult)
        elif dResult["status"] == sExpected:
            lKnown.append(dResult)
        else:
            lNew.append(dResult)
    return lNew, lKnown, lResolved


def load_projects(sFileName, lNames):
    with open(sFileName, encoding="utf-8") as oFile:
        lProjects = yaml.safe_load(oFile)["projects"]
    if lNames:
        lUnknown = sorted(set(lNames) - {d["name"] for d in lProjects})
        if lUnknown:
            raise SystemExit(f"Unknown project(s): {', '.join(lUnknown)}")
        lProjects = [d for d in lProjects if d["name"] in lNames]
    for dProject in lProjects:
        for sFile, sStatus in (dProject.get("known_issues") or {}).items():
            if sStatus not in STATUSES:
                raise SystemExit(f"{dProject['name']}: unknown status {sStatus} for {sFile}")
    return lProjects


def run_project(dProject, sCache, iJobs, iTimeout, bVerbose):
    sDirectory = fetch_project(dProject, sCache)
    lFiles = find_vhdl_files(sDirectory, dProject.get("exclude") or [])
    print(f"{dProject['name']}: checking {len(lFiles)} files", flush=True)
    lResults = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=iJobs) as oPool:
        dFutures = {oPool.submit(check_file_isolated, sFile, iTimeout): sFile for sFile in lFiles}
        for oFuture in concurrent.futures.as_completed(dFutures):
            sRelative = relative_path(dFutures[oFuture], sDirectory)
            sStatus, sDetails = oFuture.result()
            lResults.append({"file": sRelative, "status": sStatus, "details": sDetails})
            if bVerbose or sStatus != OK:
                print(f"  {sStatus:<16} {sRelative}", flush=True)
    lResults.sort(key=lambda d: d["file"])
    return lResults


def print_details(dResult, iLines=8):
    lLines = [s for s in dResult["details"].splitlines() if s.strip()]
    for sLine in lLines[:iLines]:
        print(f"      {sLine}")
    if len(lLines) > iLines:
        print(f"      ... {len(lLines) - iLines} more lines")


def parse_arguments(lArguments=None):
    oParser = argparse.ArgumentParser(description="Run mhsg over pinned open source VHDL projects.")
    oParser.add_argument("--projects", default=DEFAULT_PROJECTS, help="project list (default: %(default)s)")
    oParser.add_argument("--project", action="append", default=[], help="only run this project; can be repeated")
    oParser.add_argument("--cache", default=DEFAULT_CACHE, help="where projects are cloned (default: %(default)s)")
    oParser.add_argument("--jobs", "-j", type=int, default=os.cpu_count() or 1, help="files checked in parallel")
    oParser.add_argument("--timeout", type=int, default=600, help="seconds allowed for each mhsg run")
    oParser.add_argument("--json", help="write every result to this JSON file")
    oParser.add_argument("--verbose", "-v", action="store_true", help="also list files that pass")
    return oParser.parse_args(lArguments)


def main(lArguments=None):
    oArgs = parse_arguments(lArguments)
    lProjects = load_projects(oArgs.projects, oArgs.project)

    dReport = {}
    lAllNew = []
    lAllResolved = []
    for dProject in lProjects:
        lResults = run_project(dProject, oArgs.cache, oArgs.jobs, oArgs.timeout, oArgs.verbose)
        lNew, lKnown, lResolved = compare_with_known(lResults, dProject.get("known_issues") or {})
        dCounts = {s: sum(1 for d in lResults if d["status"] == s) for s in STATUSES}
        dReport[dProject["name"]] = {"commit": dProject["commit"], "counts": dCounts, "results": lResults}
        lAllNew.extend((dProject["name"], d) for d in lNew)
        lAllResolved.extend((dProject["name"], d) for d in lResolved)
        sCounts = ", ".join(f"{s} {i}" for s, i in dCounts.items() if i)
        print(f"{dProject['name']}: {sCounts} ({len(lKnown)} known)", flush=True)

    if oArgs.json:
        with open(oArgs.json, "w", encoding="utf-8") as oFile:
            json.dump(dReport, oFile, indent=2)

    print()
    if lAllResolved:
        print("Known issues that no longer occur (remove them from the project list):")
        for sName, dResult in lAllResolved:
            print(f"  {sName}: {dResult['file']}")
    if lAllNew:
        print("New failures:")
        for sName, dResult in lAllNew:
            print(f"  {dResult['status']:<16} {sName}: {dResult['file']}")
            print_details(dResult)
        return 1
    print("No new failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
