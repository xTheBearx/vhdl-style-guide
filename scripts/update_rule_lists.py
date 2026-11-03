#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updates the documentation generated from the rules: the page of each rule group (docs/<group>_rules.rst), the lists
of rules on the rule group pages (docs/rule_groups), the list of rules disabled by default
(docs/configuring_disabled_rules.rst) and the SystemVerilog section of docs/unfixable_rules.rst.

Run it from the root of the repository after adding or changing rules:

    uv run python scripts/update_rule_lists.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mhsg import (  # noqa: E402 pylint: disable=wrong-import-position
    __rule_doc_gen__,
    rule_list,
    vhdlFile,
)

DOCS = "docs"


def link(oRule, sPrefix=""):
    sAnchor = oRule.unique_id.replace("_", "-")
    return f"* `{oRule.unique_id} <{sPrefix}{oRule.name}_rules.html#{sAnchor}>`_"


def listed_rules(sFileName, sAfter):
    """The rules listed after the line starting with sAfter, in every list that follows it."""
    with open(sFileName, encoding="utf-8") as oFile:
        lFile = oFile.read().split("\n")
    iStart = next(i for i, s in enumerate(lFile) if s.startswith(sAfter))
    return [s.split()[1][1:] for s in lFile[iStart:] if s.startswith("* `")]


def replace_list(sFileName, lLines, sAfter=None):
    """Replaces the first block of list lines in a file, after the line starting with sAfter if given."""
    with open(sFileName, encoding="utf-8") as oFile:
        lFile = oFile.read().split("\n")
    iStart = 0
    if sAfter is not None:
        iStart = next(i for i, s in enumerate(lFile) if s.startswith(sAfter))
    iFirst = next(i for i in range(iStart, len(lFile)) if lFile[i].startswith("* `"))
    iLast = iFirst
    while iLast < len(lFile) and lFile[iLast].startswith("* `"):
        iLast += 1
    # Lines already in the list are kept as they are; new rules get a new line
    dExisting = {sLine.split()[1][1:]: sLine for sLine in lFile[iFirst:iLast]}
    lFile[iFirst:iLast] = [dExisting.get(sLine.split()[1][1:], sLine) for sLine in lLines]
    with open(sFileName, "w", encoding="utf-8") as oFile:
        oFile.write("\n".join(lFile))


def update_rules_index(lNames):
    """Lists the pages of the SystemVerilog rule groups in the last toctree of docs/rules.rst."""
    sFileName = os.path.join(DOCS, "rules.rst")
    with open(sFileName, encoding="utf-8") as oFile:
        sText = oFile.read()
    iStart = sText.index("\nSystemVerilog and Verilog\n")
    iTree = sText.index(":maxdepth: 2\n", iStart) + len(":maxdepth: 2\n")
    sText = sText[:iTree] + "\n" + "".join(f"   {s}_rules.rst\n" for s in lNames)
    with open(sFileName, "w", encoding="utf-8") as oFile:
        oFile.write(sText)


def main():
    oRules = rule_list.rule_list(vhdlFile.vhdlFile([""]), None, None, bAllLanguages=True)
    lRules = [o for o in oRules.rules if not o.deprecated]
    __rule_doc_gen__.create_rule_documentation(DOCS)
    dGroups = {}
    for oRule in lRules:
        for sGroup in oRule.groups:
            dGroups.setdefault(sGroup, []).append(oRule)
    for sGroup, lGroupRules in dGroups.items():
        sFileName = os.path.join(DOCS, "rule_groups", sGroup.replace("::", "_") + "_rule_group.rst")
        if os.path.exists(sFileName) and listed_rules(sFileName, "Rules Enforcing") != [o.unique_id for o in lGroupRules]:
            replace_list(sFileName, [link(o, "../") for o in lGroupRules], "Rules Enforcing")
    replace_list(os.path.join(DOCS, "configuring_disabled_rules.rst"), [link(o) for o in lRules if o.disable], "Rules Disabled by Default")
    update_rules_index(sorted({o.name for o in lRules if o.name.startswith("sv_")}))
    lUnfixable = [link(o) for o in lRules if not o.fixable and not o.proposed and o.name.startswith("sv_")]
    sFileName = os.path.join(DOCS, "unfixable_rules.rst")
    with open(sFileName, encoding="utf-8") as oFile:
        sText = oFile.read()
    sSection = "SystemVerilog Rules\n-------------------\n\nRules on the design of SystemVerilog and Verilog code that only the designer can change.\n\n"
    sText = re.sub(r"\nSystemVerilog( Rules)?\n-+\n.*?(?=\n[^\n]+\n-+\n|\Z)", "", sText, flags=re.S).rstrip("\n") + "\n"
    if lUnfixable:
        sText += "\n" + sSection + "\n".join(lUnfixable) + "\n"
    with open(sFileName, "w", encoding="utf-8") as oFile:
        oFile.write(sText)


if __name__ == "__main__":
    main()
