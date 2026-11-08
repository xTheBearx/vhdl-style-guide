# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule
from mhsg.rules import hierarchy_names

reSimpleName = re.compile(r"^[a-z][a-z0-9_]*$")


class rule_040(Rule):
    """
    This rule checks that a signal connected to a port of an instance has the name of the port, apart from
    prefixes and suffixes, so a signal keeps its name through the hierarchy.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (DR9).

    A signal renamed at each level of the hierarchy is hard to follow from the top to the bottom of the design. The
    strip_prefixes and strip_suffixes options list the parts that are ignored, such as i\\_ and _o, which mark direction or kind;
    one prefix and one suffix, the longest that fits, are removed and the names compared ignoring case. The defaults
    are those of sv_module_018, so a signal is compared with its port the same way in VHDL and SystemVerilog: they
    include the suffixes of port names written by direction, _i, _o and _io, with _n or n before them for active
    low ports, so rst_n_i or rst_ni matches rst_n. Only port maps that connect a signal by name, not a slice or an
    expression, are checked.

    The ports of an entity or component instantiated more than once are not checked: each instance connects its own
    signals, which cannot all have the names of the ports. The instances of the files of the run and of the index
    files are counted; an instance in a for generate counts as more than one. This is
    what sv_module_018 does for SystemVerilog.

    **Violation**

    .. code-block:: vhdl

       u_fifo : entity work.fifo
         port map (
           wr_data => payload
         );

    **Fix**

    .. code-block:: vhdl

       u_fifo : entity work.fifo
         port map (
           wr_data => wr_data
         );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Name the signal after the port"
        # The defaults of sv_module_018 too, see hierarchy_names.py
        self.strip_prefixes = list(hierarchy_names.STRIP_PREFIXES)
        self.configuration.append("strip_prefixes")
        self.strip_suffixes = list(hierarchy_names.STRIP_SUFFIXES)
        self.configuration.append("strip_suffixes")

    def check(self, oModel, oFile):
        dInstances = instance_counts(oModel, oFile)
        for oArchitecture in oModel.architectures:
            for oInstance in oArchitecture.instances:
                if dInstances.get(oInstance.unit, 0) > 1:
                    continue
                for sFormal, sActual, iLine in oInstance.associations:
                    if sFormal is None or not reSimpleName.match(sActual) or sActual == "open":
                        continue
                    if self.stem(sFormal) != self.stem(sActual):
                        iIndex = formal_index(oFile.lAllObjects, oInstance, sFormal, iLine)
                        self.report(oFile, iIndex, f"Signal {sActual} connected to port {sFormal} of {oInstance.label} has another name")

    def stem(self, sName):
        """The name in lower case without one of the prefixes and one of the suffixes, see hierarchy_names.py."""
        return hierarchy_names.stem(sName, self.strip_prefixes, self.strip_suffixes)


def instance_counts(oModel, oFile):
    """
    {lower case unit name: number of instances}: of the files of the run and the index files, in lint mode, see
    project_index.py, and of the file, whichever is more.
    """
    dReturn = {}
    for oArchitecture in oModel.architectures:
        for oInstance in oArchitecture.instances:
            bLoop = any(model.kind(oModel.lTokens[iIndex]) == ("for_generate_statement", "for_keyword") for iIndex, _ in oInstance.generate)
            dReturn[oInstance.unit] = dReturn.get(oInstance.unit, 0) + (2 if bLoop else 1)
    dProject = getattr(getattr(oFile, "configuration", None), "project_instance_counts", None) or {}
    for sUnit, iCount in dProject.items():
        dReturn[sUnit] = max(iCount, dReturn.get(sUnit, 0))
    return dReturn


def formal_index(lTokens, oInstance, sFormal, iLine):
    """Returns the token index of the formal part of an association on a line of an instance, or of the instance."""
    iCurrent = oInstance.line
    for iIndex in range(oInstance.index, len(lTokens)):
        oToken = lTokens[iIndex]
        if isinstance(oToken, model.parser.carriage_return):
            iCurrent += 1
        elif iCurrent == iLine and model.kind(oToken) == ("association_element", "formal_part") and (oToken.get_value() or "").lower() == sFormal:
            return iIndex
        elif model.kind(oToken) == ("component_instantiation_statement", "semicolon"):
            break
    return oInstance.index
