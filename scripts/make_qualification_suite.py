# -*- coding: utf-8 -*-
"""
Makes the qualification suites in mhsg/qualification, one for each built in rule set, see mhsg/qualify.py.

For each rule of a rule set the suite takes examples from the test inputs of MHSG: the inputs of the rule's tests,
with their fixed versions as examples that pass, the SystemVerilog test inputs on which the rule reports something,
and for rules that have no test input, the examples in scripts/qualification_examples. The rules of design analysis
run on the test designs listed in DESIGNS. The examples are copied into mhsg/qualification/examples, MHSG is run on
each in lint mode with the rule set, and what each rule finds is recorded as its expected result.

Review the differences of the manifests before committing them: they are the expected results of the qualification.

    python scripts/make_qualification_suite.py [rule set ...]
"""

import concurrent.futures
import copy
import glob
import importlib
import os
import shutil
import sys

import yaml

sRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, sRoot)

from mhsg import qualify, rule_list, rule_set, vhdlFile  # noqa: E402

TESTS = os.path.join(sRoot, "tests")
EXTRA = os.path.join(sRoot, "scripts", "qualification_examples")
EXAMPLES = os.path.join(qualify.DIRECTORY, "examples")

# Rules whose examples are the test inputs of other rules
SHARED_INPUTS = {"lint_004": "lint/rule_003_test_input.vhd", "lint_006": "lint/rule_005_test_input.vhd", "lint_007": "lint/rule_005_test_input.vhd"}

# The test designs the rules of design analysis run on: name, design section with files in tests/design
DESIGNS = [
    ("clean design", {"top": "clean_top", "libraries": [{"name": "work", "files": ["clean.vhd"]}]}),
    ("undeclared signal", {"top": "undeclared_top", "libraries": [{"name": "work", "files": ["undeclared.vhd"]}]}),
    ("latch", {"top": "latch_top", "libraries": [{"name": "work", "files": ["latch.vhd"]}]}),
    ("combinational loop", {"top": "loop_top", "libraries": [{"name": "work", "files": ["loop.vhd"]}]}),
    ("multiple drivers", {"top": "md_top", "libraries": [{"name": "work", "files": ["multiple_drivers.vhd"]}]}),
    ("registers", {"top": "registers_top", "libraries": [{"name": "work", "files": ["registers.vhd"]}]}),
    ("logic depth", {"top": "depth_top", "libraries": [{"name": "work", "files": ["depth.vhd"]}]}),
    ("clock domain crossings", {"top": "cdc_top", "libraries": [{"name": "work", "files": ["cdc.vhd"]}]}),
    ("reconvergence", {"top": "reconvergence_top", "libraries": [{"name": "work", "files": ["reconvergence.vhd"]}]}),
    ("black box", {"top": "bb_top", "libraries": [{"name": "work", "files": ["black_box.vhd"]}]}),
    ("deep logic", {"top": "deep_top", "libraries": [{"name": "work", "files": ["extra:design_007/deep.vhd"]}]}),
]


_dFolders = {}


def rule_folder(sRule):
    """The folder of a rule's module under mhsg/rules, such as if_statement for if_022."""
    if not _dFolders:
        oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), None, None, bAllLanguages=True)
        for oRule in oRules.rules:
            _dFolders[oRule.get_unique_id()] = type(oRule).__module__.split(".")[-2]
    return _dFolders.get(sRule)


def copy_example(sSource):
    """Copies a test input into the examples and returns its path in the qualification directory."""
    sRelative = os.path.relpath(sSource, TESTS) if sSource.startswith(TESTS) else os.path.join("extra", os.path.relpath(sSource, EXTRA))
    sTarget = os.path.join(EXAMPLES, sRelative)
    os.makedirs(os.path.dirname(sTarget), exist_ok=True)
    shutil.copyfile(sSource, sTarget)
    return os.path.relpath(sTarget, qualify.DIRECTORY)


def design_file(sName):
    """The path of a file of a test design: in tests/design, or in the examples written for qualification with extra:."""
    if sName.startswith("extra:"):
        return os.path.join(EXTRA, sName[len("extra:") :])
    return os.path.join(TESTS, "design", sName)


def vhdl_examples(sRule):
    if sRule in SHARED_INPUTS:
        return [os.path.join(TESTS, SHARED_INPUTS[sRule])]
    sFolder = rule_folder(sRule)
    sNumber = sRule.rsplit("_", 1)[1]
    lFiles = sorted(glob.glob(os.path.join(TESTS, sFolder or "-", f"rule_{sNumber}_test_input*.vhd")))
    lFiles += sorted(glob.glob(os.path.join(EXTRA, sRule, "*.vhd")))
    return lFiles


def sv_examples():
    return sorted(glob.glob(os.path.join(TESTS, "svfile", "*.sv")) + glob.glob(os.path.join(TESTS, "svfile", "**", "*.sv")))


def make(sRuleSet):
    oRuleSet = rule_set.load(sRuleSet)
    lRules = sorted({sRule for oSet in oRuleSet.all_sets() for oCheck in oSet.checks for sRule in oCheck.rules})
    dResults = {}

    def findings(sExample):
        if sExample not in dResults:
            dResults[sExample] = qualify.run_file(sRuleSet, os.path.join(qualify.DIRECTORY, sExample)) or {}
        return dResults[sExample]

    # Every example the rules may use runs first, in parallel, as each run takes a second or two
    lAll = [copy_example(s) for s in sv_examples()] if any(s.startswith("sv_") for s in lRules) else []
    for sRule in lRules:
        if not sRule.startswith(("sv_", "design_")):
            lAll += [copy_example(s) for s in vhdl_examples(sRule)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as oPool:
        lAll = sorted(set(lAll))
        for sExample, dFound in zip(lAll, oPool.map(lambda s: qualify.run_file(sRuleSet, os.path.join(qualify.DIRECTORY, s)), lAll)):
            dResults[sExample] = dFound or {}

    lCases = []
    lSvExamples = None
    for sRule in lRules:
        if sRule.startswith("design_"):
            continue
        if sRule.startswith("sv_"):
            if lSvExamples is None:
                lSvExamples = [copy_example(s) for s in sv_examples()]
            lFailing = [s for s in lSvExamples if findings(s).get(sRule)][:3]
            lPassing = [s for s in lSvExamples if not findings(s).get(sRule)][:1]
            lExamples = lFailing + lPassing + [copy_example(s) for s in sorted(glob.glob(os.path.join(EXTRA, sRule, "*.sv")))]
        else:
            lExamples = [copy_example(s) for s in vhdl_examples(sRule)]
        for sExample in lExamples:
            lCases.append({"rule": sRule, "file": sExample, "expected": findings(sExample).get(sRule, [])})
    lDesignCases = []
    lDesignRules = [s for s in lRules if s.startswith("design_")]
    if lDesignRules:
        for sName, dDesign in copy.deepcopy(DESIGNS):
            for dLibrary in dDesign["libraries"]:
                dLibrary["files"] = [copy_example(design_file(s)) for s in dLibrary["files"]]
            dFound = qualify.run_design(sRuleSet, dDesign) or {}
            for sRule in lDesignRules:
                lDesignCases.append({"rule": sRule, "name": sName, "design": dDesign, "expected": dFound.get(sRule, [])})
    dManifest = {
        "rule_set": oRuleSet.name,
        "rule_set_version": oRuleSet.version,
        "cases": lCases,
        "design_cases": lDesignCases,
    }
    with open(qualify.manifest_file(sRuleSet), "w", encoding="utf-8") as oFile:
        oFile.write(f"# Qualification suite of the {oRuleSet.name} rule set, made by scripts/make_qualification_suite.py.\n")
        oFile.write("# The expected results were reviewed before they were committed; see mhsg/qualify.py.\n")
        yaml.safe_dump(dManifest, oFile, sort_keys=False, width=200, allow_unicode=True)
    lCovered = {d["rule"] for d in lCases + lDesignCases}
    print(f"{sRuleSet}: {len(lCases)} cases, {len(lDesignCases)} design cases; rules without examples: {[s for s in lRules if s not in lCovered]}")


def main():
    os.makedirs(qualify.DIRECTORY, exist_ok=True)
    for sRuleSet in sys.argv[1:] or rule_set.get_built_in_rule_sets():
        make(sRuleSet)


if __name__ == "__main__":
    importlib.invalidate_caches()
    main()
