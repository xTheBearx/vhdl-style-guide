# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule

reSimpleName = re.compile(r"^[a-z][a-z0-9_]*$")


class rule_040(Rule):
    """
    This rule checks that a signal connected to a port of an instance has the name of the port, apart from
    prefixes and suffixes, so a signal keeps its name through the hierarchy.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (DR9).

    A signal renamed at each level of the hierarchy is hard to follow from the top to the bottom of the design. The
    strip_prefixes and strip_suffixes options list the parts that are ignored, such as i\\_ and _o, which mark direction or kind.
    Only port maps that connect a signal by name, not a slice or an expression, are checked.

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
        self.strip_prefixes = ["i_", "o_", "io_", "s_", "r_", "w_"]
        self.configuration.append("strip_prefixes")
        self.strip_suffixes = ["_i", "_o", "_io", "_s", "_r", "_n", "_reg", "_sig"]
        self.configuration.append("strip_suffixes")

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oInstance in oArchitecture.instances:
                for sFormal, sActual, iLine in oInstance.associations:
                    if sFormal is None or not reSimpleName.match(sActual) or sActual == "open":
                        continue
                    if self.stem(sFormal) != self.stem(sActual):
                        iIndex = formal_index(oFile.lAllObjects, oInstance, sFormal, iLine)
                        self.report(oFile, iIndex, f"Signal {sActual} connected to port {sFormal} of {oInstance.label} has another name")

    def stem(self, sName):
        """The name without one of the prefixes and one of the suffixes."""
        for sPrefix in sorted(self.strip_prefixes, key=len, reverse=True):
            if sName.startswith(sPrefix.lower()) and len(sName) > len(sPrefix):
                sName = sName[len(sPrefix) :]
                break
        for sSuffix in sorted(self.strip_suffixes, key=len, reverse=True):
            if sName.endswith(sSuffix.lower()) and len(sName) > len(sSuffix):
                sName = sName[: -len(sSuffix)]
                break
        return sName


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
