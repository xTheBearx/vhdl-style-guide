# -*- coding: utf-8 -*-
"""
Base class of the lint rules.
"""

from mhsg import rule, violation
from mhsg.vhdlFile.extract import tokens

SIGNAL_KINDS = ("signal", "port")


class Rule(rule.Rule):
    """
    A lint rule reports a problem in the design instead of its formatting. It never changes the code.
    Lint rules are disabled by default and run in lint mode, see rule_set.py, in a pass before the phases.
    Subclasses implement check(oModel, oFile).
    """

    def __init__(self):
        super().__init__()
        self.lint = True
        self.disable = True
        self.fixable = False
        self.phase = 7
        self.groups.append("lint")
        self.configuration_documentation_link = None

    def analyze(self, oFile):
        self._print_debug_message("Analyzing rule: " + self.unique_id)
        self.check(oFile.get_lint_model(), oFile)

    def check(self, oModel, oFile):
        """Adds a violation for each problem found in the model of the file."""

    def report(self, oFile, iIndex, sSolution):
        """Adds a violation at the token index, so a code tag on that line can disable it."""
        iLine = oFile.get_token_map().get_line_number_of_index(iIndex)
        oToi = tokens.New(iIndex, iLine, [oFile.lAllObjects[iIndex]])
        self.add_violation(violation.New(iLine, oToi, sSolution))


def signal_kind(oFile, oArchitecture, sName, iIndex):
    """
    Returns "signal" or "port" for a name that is a signal or port at the token index, "other" for any
    other declaration, and None if the name is not declared in the file or the ports of the entity.
    """
    lDeclarations = oFile.get_declarations().find(sName, iIndex)
    if lDeclarations:
        sKind = lDeclarations[0].kind
        return sKind if sKind in SIGNAL_KINDS else "other"
    for sPort, sMode in entity_ports(oFile, oArchitecture):
        if sPort == sName:
            return "port"
    return None


def entity_ports(oFile, oArchitecture):
    """
    Returns the (name, mode) pairs of the ports of the entity of an architecture, from the file or from
    the other files of the run, or an empty list if they are not known.
    """
    oModel = oFile.get_lint_model()
    if oArchitecture.entity in oModel.entity_ports:
        return [(sName, sMode) for sName, sMode, iLine in oModel.entity_ports[oArchitecture.entity]]
    dProject = getattr(getattr(oFile, "configuration", None), "project_port_modes", None) or {}
    return list((dProject.get("entity") or {}).get(oArchitecture.entity) or [])


def unit_ports(oFile, oInstance):
    """
    Returns the (name, mode) pairs of the ports of an instantiated entity or component, or None if they are not known.
    A component is looked up in the file first; an entity or component then in the other files of the run.
    """
    oModel = oFile.get_lint_model()
    dLocal = oModel.entity_ports if oInstance.unit_kind == "entity" else oModel.component_ports
    if oInstance.unit in dLocal:
        return [(sName, sMode) for sName, sMode, iLine in dLocal[oInstance.unit]]
    dProject = getattr(getattr(oFile, "configuration", None), "project_port_modes", None) or {}
    lPorts = (dProject.get(oInstance.unit_kind) or {}).get(oInstance.unit)
    if lPorts is None and oInstance.unit_kind == "component":
        # A component usually has the ports of the entity of the same name
        lPorts = (dProject.get("entity") or {}).get(oInstance.unit)
    return None if lPorts is None else list(lPorts)
