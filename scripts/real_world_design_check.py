#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run design analysis (mhsg --design) on configurations of the open source projects of the real world check.

The designs, and the findings they are known to have, are listed in scripts/real_world_designs.yaml. A design that
requires read_slang, the SystemVerilog reader of the yosys-slang plugin, is skipped when Yosys does not have it. The projects
are fetched like scripts/real_world_check.py does. The run fails when a design has a finding that is not listed
as known, or when design analysis does not run. Known findings that are no longer found are reported, so the list
can be updated.

Needs GHDL, Yosys and the GHDL plugin for Yosys.

Example:

  python scripts/real_world_design_check.py --design neorv32_top
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import real_world_check  # noqa: E402  pylint: disable=wrong-import-position

DEFAULT_DESIGNS = os.path.join(real_world_check.REPO_ROOT, "scripts", "real_world_designs.yaml")


def run_design(dDesign, sProjectDirectory, iTimeout):
    """Runs design analysis on a design and returns (exit status, findings, other output lines, seconds)."""
    dEnvironment = dict(os.environ)
    for sName, sValue in (dDesign.get("environment") or {}).items():
        # Relative to the project root, which is the working directory of the run
        dEnvironment[sName] = str(sValue)
    with tempfile.TemporaryDirectory(prefix="mhsg_design_check_") as sDirectory:
        sConfiguration = os.path.join(sDirectory, "design.yaml")
        with open(sConfiguration, "w", encoding="utf-8") as oFile:
            yaml.safe_dump({"design": dDesign["design"]}, oFile)
        fStart = time.time()
        try:
            oProcess = subprocess.run(
                [sys.executable, real_world_check.MHSG, "--design", "-c", sConfiguration, "-of", "syntastic"],
                cwd=sProjectDirectory,
                env=dEnvironment,
                capture_output=True,
                text=True,
                timeout=iTimeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return None, [], ["TIMEOUT"], time.time() - fStart
    fSeconds = time.time() - fStart
    lFindings = []
    lOther = []
    for sLine in (oProcess.stdout + oProcess.stderr).splitlines():
        if sLine.startswith(("ERROR: ", "WARNING: ", "NOTE: ")) and ")design_" in sLine:
            lFindings.append(sLine.split(": ", 1)[1])
        elif sLine.strip():
            lOther.append(sLine)
    return oProcess.returncode, lFindings, lOther, fSeconds


def available_tools():
    """The optional tools designs can require: read_slang, when Yosys has the yosys-slang plugin."""
    if real_world_check.REPO_ROOT not in sys.path:
        sys.path.insert(0, real_world_check.REPO_ROOT)
    from mhsg.design import tools  # noqa: E402  pylint: disable=import-outside-toplevel

    sYosys = shutil.which("yosys")
    return {"read_slang"} if sYosys and tools.has_slang(sYosys) else set()


def main(lArguments=None):
    oParser = argparse.ArgumentParser(description="Run design analysis on real world designs and compare the findings with the known ones.")
    oParser.add_argument("--designs", default=DEFAULT_DESIGNS, help="design list (default: %(default)s)")
    oParser.add_argument("--projects", default=real_world_check.DEFAULT_PROJECTS, help="project list (default: %(default)s)")
    oParser.add_argument("--cache", default=real_world_check.DEFAULT_CACHE, help="where the projects are cloned (default: %(default)s)")
    oParser.add_argument("--design", action="append", default=[], help="only run this design; can be repeated")
    oParser.add_argument("--timeout", type=int, default=600, help="time limit per design in seconds (default: %(default)s)")
    oArguments = oParser.parse_args(lArguments)

    with open(oArguments.designs, encoding="utf-8") as oFile:
        lDesigns = yaml.safe_load(oFile)["designs"]
    if oArguments.design:
        lUnknown = sorted(set(oArguments.design) - {d["name"] for d in lDesigns})
        if lUnknown:
            raise SystemExit(f"unknown designs: {', '.join(lUnknown)}")
        lDesigns = [d for d in lDesigns if d["name"] in oArguments.design]
    dProjects = {d["name"]: d for d in real_world_check.load_projects(oArguments.projects, [])}

    bFailed = False
    setTools = available_tools()
    for dDesign in lDesigns:
        lMissing = [s for s in dDesign.get("requires") or [] if s not in setTools]
        if lMissing:
            print(f"{dDesign['name']}: skipped, needs {', '.join(lMissing)}", flush=True)
            continue
        dProject = dProjects[dDesign["project"]]
        sProjectDirectory = real_world_check.fetch_project(dProject, oArguments.cache)
        iStatus, lFindings, lOther, fSeconds = run_design(dDesign, sProjectDirectory, oArguments.timeout)
        lKnown = list(dDesign.get("known") or [])
        lNew = [s for s in lFindings if s not in lKnown]
        lResolved = [s for s in lKnown if s not in lFindings]
        bRan = iStatus in (0, 1) and not lOther
        print(f"{dDesign['name']}: {len(lFindings)} findings, {len(lNew)} new, {len(lResolved)} resolved, {fSeconds:.1f} s", flush=True)
        for sLine in lOther:
            print(f"  output: {sLine}")
        for sLine in lNew:
            print(f"  new: {sLine}")
        for sLine in lResolved:
            print(f"  resolved: {sLine}")
        bFailed = bFailed or bool(lNew) or not bRan
    return 1 if bFailed else 0


if __name__ == "__main__":
    sys.exit(main())
