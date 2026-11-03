# -*- coding: utf-8 -*-
"""
Declarations of black boxes: instances whose logic design analysis cannot see, such as vendor primitives, vendor
macros, encrypted IP or modules in other languages.

Nothing is assumed about a black box. The user declares the effect of each port on clock domain crossings with a
role, in the black_boxes part of the design section, in shared library files, or for single instances:

    black_boxes:
      BUFGCE:
        archetype: clock_buffer
        input: I
        output: O
        enable: CE
        reference: UG953, BUFGCE
      vendor_dma:
        reviewed_by: H. Reid
        ports:
          aclk: clock
          s_axi_*: {sync: aclk}
          irq: async
          cfg_mode: {static: Written once at boot, before aclk starts}

Roles:
  clock                                     a clock input
  {sync: <clock pin>}                       data timed by a clock pin of the box
  {path: [<inputs>]}                        an output that follows inputs through logic, without a register
  {clock_out: {from: <pin>, relation: r}}   a clock output: same (a buffer), derived (synchronous to the input) or
                                            independent (a new asynchronous clock)
  {enable: <clock output>}                  the enable of a clock buffer
  {reset_in: async} or {reset_in: {sync: <clock pin>}}
  {reset_out: {clock: <pin>, release: sync | async}}
  async                                     an output that changes, or an input sampled, asynchronously
  {synchronized: {clock: <pin>, from: <input>, stages: <number or generic>}}
                                            an output the box synchronizes inside; listed for manual review
  {static: <justification>}                 configuration that only changes while idle; needs reviewed_by
  unused                                    a port with no effect on clock domains

Archetypes expand to roles from a few names, see ARCHETYPES. A port that another role names, such as the input of a
path, needs no role of its own.
"""

import fnmatch
import os

import yaml

from mhsg import exceptions
from mhsg.design import graph

SIMPLE_ROLES = ("clock", "async", "unused")
DICT_ROLES = ("sync", "path", "clock_out", "enable", "reset_in", "reset_out", "synchronized", "static")
RELATIONS = ("same", "derived", "independent")
MISSING = "TODO"
DECLARATION_KEYS = ("archetype", "ports", "reference", "reviewed_by", "variants", "justification")


class Role:
    def __init__(self, sKind, **dValues):
        self.kind = sKind
        self.clock = dValues.get("clock")
        self.inputs = dValues.get("inputs", [])
        self.source = dValues.get("source")
        self.relation = dValues.get("relation")
        self.release = dValues.get("release")
        self.target = dValues.get("target")
        self.stages = dValues.get("stages")
        self.justification = dValues.get("justification")
        self.reviewed_by = dValues.get("reviewed_by")
        self.asynchronous = dValues.get("asynchronous", False)

    def names(self):
        """The other ports this role names, which then need no role of their own."""
        return [s for s in [self.source, self.target] + list(self.inputs) if s]

    def __repr__(self):
        return self.kind


def parse_role(oValue, sWhere):
    """Returns the Role written as a string or a single key map, or raises a ConfigurationError."""
    if isinstance(oValue, str):
        if oValue in SIMPLE_ROLES:
            return Role(oValue)
        if oValue == MISSING:
            return None
        raise exceptions.ConfigurationError(f"ERROR: {sWhere}: unknown role {oValue}; expected one of {', '.join(SIMPLE_ROLES + DICT_ROLES)}")
    if not isinstance(oValue, dict) or len(oValue) != 1:
        raise exceptions.ConfigurationError(f"ERROR: {sWhere}: a role is a name, such as clock, or a map with one key, such as sync: clk")
    sKind, oArgument = next(iter(oValue.items()))
    if sKind == "sync":
        return Role("sync", clock=str(oArgument))
    if sKind == "path":
        return Role("path", inputs=[str(s) for s in (oArgument if isinstance(oArgument, list) else [oArgument])])
    if sKind == "enable":
        return Role("enable", target=str(oArgument))
    if sKind == "clock_out":
        dArgument = oArgument if isinstance(oArgument, dict) else {}
        sRelation = str(dArgument.get("relation", ""))
        if "from" not in dArgument and sRelation != "independent" or sRelation not in RELATIONS:
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: clock_out needs from, a clock input, and relation, one of {', '.join(RELATIONS)}")
        return Role("clock_out", source=str(dArgument["from"]) if "from" in dArgument else None, relation=sRelation)
    if sKind == "reset_in":
        if oArgument == "async":
            return Role("reset_in", asynchronous=True)
        if isinstance(oArgument, dict) and "sync" in oArgument:
            return Role("reset_in", clock=str(oArgument["sync"]))
        raise exceptions.ConfigurationError(f"ERROR: {sWhere}: reset_in is async or a map with sync: <clock pin>")
    if sKind == "reset_out":
        dArgument = oArgument if isinstance(oArgument, dict) else {}
        if "clock" not in dArgument or dArgument.get("release") not in ("sync", "async"):
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: reset_out needs clock, a clock pin, and release, sync or async")
        return Role("reset_out", clock=str(dArgument["clock"]), release=dArgument["release"])
    if sKind == "synchronized":
        dArgument = oArgument if isinstance(oArgument, dict) else {}
        if "clock" not in dArgument:
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: synchronized needs clock, the clock pin of the output, and from, the input")
        return Role(
            "synchronized",
            clock=str(dArgument["clock"]),
            source=str(dArgument["from"]) if dArgument.get("from") else None,
            stages=dArgument.get("stages"),
        )
    if sKind == "static":
        if isinstance(oArgument, dict):
            return Role("static", justification=str(oArgument.get("justification") or "").strip(), reviewed_by=str(oArgument.get("reviewed_by") or "").strip())
        return Role("static", justification=str(oArgument or "").strip())
    raise exceptions.ConfigurationError(f"ERROR: {sWhere}: unknown role {sKind}; expected one of {', '.join(SIMPLE_ROLES + DICT_ROLES)}")


def as_list(oValue):
    if oValue is None:
        return []
    return [str(s) for s in oValue] if isinstance(oValue, list) else [str(oValue)]


def expand_archetype(dDeclaration, sWhere):
    """Returns the ports map, port name or pattern to role, of an archetype and its parameters."""
    sArchetype = dDeclaration.get("archetype")

    def need(*lNames):
        for sName in lNames:
            if not dDeclaration.get(sName):
                raise exceptions.ConfigurationError(f"ERROR: {sWhere}: archetype {sArchetype} needs {', '.join(lNames)}")

    dPorts = {}
    if sArchetype == "buffer":
        need("input", "output")
        for sOutput in as_list(dDeclaration["output"]):
            dPorts[sOutput] = {"path": as_list(dDeclaration["input"])}
    elif sArchetype == "clock_buffer":
        need("input", "output")
        dPorts[str(dDeclaration["input"])] = "clock"
        dPorts[str(dDeclaration["output"])] = {"clock_out": {"from": str(dDeclaration["input"]), "relation": "same"}}
        for sEnable in as_list(dDeclaration.get("enable")):
            dPorts[sEnable] = {"enable": str(dDeclaration["output"])}
    elif sArchetype == "clock_generator":
        need("input", "outputs")
        sRelation = str(dDeclaration.get("relation", "derived"))
        dPorts[str(dDeclaration["input"])] = "clock"
        for sOutput in as_list(dDeclaration["outputs"]):
            dPorts[sOutput] = {"clock_out": {"from": str(dDeclaration["input"]), "relation": sRelation}}
        for sReset in as_list(dDeclaration.get("reset")):
            dPorts[sReset] = {"reset_in": "async"}
        for sLocked in as_list(dDeclaration.get("locked")):
            dPorts[sLocked] = "async"
    elif sArchetype == "single_clock":
        need("clock")
        dPorts[str(dDeclaration["clock"])] = "clock"
        for sReset in as_list(dDeclaration.get("async_reset")):
            dPorts[sReset] = {"reset_in": "async"}
        dPorts["*"] = {"sync": str(dDeclaration["clock"])}
    elif sArchetype in ("dual_clock", "memory", "dual_clock_fifo"):
        need("sides")
        dSides = dDeclaration["sides"]
        if not isinstance(dSides, dict) or len(dSides) < 2:
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: sides maps each clock pin to the ports timed by it, for two or more clocks")
        for sClock, lPorts in dSides.items():
            dPorts[str(sClock)] = "clock"
            for sPort in as_list(lPorts):
                dPorts[sPort] = {"sync": str(sClock)}
    elif sArchetype == "synchronizer":
        need("destination_clock", "input", "output")
        if dDeclaration.get("source_clock"):
            dPorts[str(dDeclaration["source_clock"])] = "clock"
            dPorts[str(dDeclaration["input"])] = {"sync": str(dDeclaration["source_clock"])}
        else:
            dPorts[str(dDeclaration["input"])] = "async"
        dPorts[str(dDeclaration["destination_clock"])] = "clock"
        dPorts[str(dDeclaration["output"])] = {
            "synchronized": {"clock": str(dDeclaration["destination_clock"]), "from": str(dDeclaration["input"]), "stages": dDeclaration.get("stages")},
        }
    elif sArchetype == "async_input":
        for sOutput in as_list(dDeclaration.get("outputs") or "*"):
            dPorts[sOutput] = "async"
    elif sArchetype == "static":
        dPorts["*"] = {"static": {"justification": dDeclaration.get("justification"), "reviewed_by": dDeclaration.get("reviewed_by")}}
    else:
        raise exceptions.ConfigurationError(f"ERROR: {sWhere}: unknown archetype {sArchetype}; expected one of {', '.join(ARCHETYPES)}")
    return dPorts


# Archetype -> its parameters
ARCHETYPES = {
    "buffer": "input, output",
    "clock_buffer": "input, output, enable",
    "clock_generator": "input, outputs, relation (derived), reset, locked",
    "single_clock": "clock, async_reset",
    "dual_clock": "sides: {clock pin: [ports]}",
    "memory": "sides: {clock pin: [ports]}",
    "dual_clock_fifo": "sides: {clock pin: [ports]}",
    "synchronizer": "source_clock, destination_clock, input, output, stages",
    "async_input": "outputs (all)",
    "static": "justification, reviewed_by",
}
ARCHETYPE_KEYS = (
    "input",
    "output",
    "outputs",
    "enable",
    "relation",
    "reset",
    "locked",
    "clock",
    "async_reset",
    "sides",
    "source_clock",
    "destination_clock",
    "stages",
)


class Declaration:
    """The declaration of a black box type, or of single instances."""

    def __init__(self, sName, dDeclaration, sSource):
        sWhere = f"black box {sName} ({sSource})"
        if not isinstance(dDeclaration, dict):
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: a declaration is a map with ports or an archetype")
        lUnknown = [s for s in dDeclaration if s not in DECLARATION_KEYS + ARCHETYPE_KEYS]
        if lUnknown:
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: unknown keys {', '.join(sorted(map(str, lUnknown)))}")
        self.name = sName
        self.source = sSource
        self.archetype = dDeclaration.get("archetype")
        self.reference = str(dDeclaration.get("reference") or "").strip()
        self.reviewed_by = str(dDeclaration.get("reviewed_by") or "").strip()
        if self.reviewed_by == MISSING:
            self.reviewed_by = ""
        if self.reference == MISSING:
            self.reference = ""
        dPorts = dict(expand_archetype(dDeclaration, sWhere)) if self.archetype else {}
        if not isinstance(dDeclaration.get("ports") or {}, dict):
            raise exceptions.ConfigurationError(f"ERROR: {sWhere}: ports maps port names or patterns to roles")
        # Ports written out take precedence over those of the archetype
        self.ports = [(str(k), parse_role(v, f"{sWhere}, port {k}")) for k, v in (dDeclaration.get("ports") or {}).items()]
        self.ports += [(str(k), parse_role(v, f"{sWhere}, port {k}")) for k, v in dPorts.items()]
        self.variants = []
        for iVariant, dVariant in enumerate(dDeclaration.get("variants") or []):
            if not isinstance(dVariant, dict) or not isinstance(dVariant.get("when"), dict):
                raise exceptions.ConfigurationError(f"ERROR: {sWhere}: each variant has when, a map of generics to values, and ports")
            lPorts = [(str(k), parse_role(v, f"{sWhere}, variant {iVariant + 1}, port {k}")) for k, v in (dVariant.get("ports") or {}).items()]
            self.variants.append(({str(k).lower(): v for k, v in dVariant["when"].items()}, lPorts))

    def port_lists(self, dGenerics):
        """The (port or pattern, role) lists that apply to an instance with these generic values, first wins."""
        lReturn = []
        for dWhen, lPorts in self.variants:
            if all(same_value(dGenerics.get(k), v) for k, v in dWhen.items()):
                lReturn.append(lPorts)
        return lReturn + [self.ports]

    def role(self, sPort, dGenerics):
        """Returns (found, role): found is False if no entry names the port; the role is None for TODO."""
        lLists = self.port_lists(dGenerics)
        for lPorts in lLists:
            for sPattern, oRole in lPorts:
                if sPattern.lower() == sPort.lower():
                    return True, oRole
        for lPorts in lLists:
            for sPattern, oRole in lPorts:
                if fnmatch.fnmatchcase(sPort.lower(), sPattern.lower()):
                    return True, oRole
        return False, None

    def referenced_ports(self, dGenerics):
        return {s.lower() for lPorts in self.port_lists(dGenerics) for _, oRole in lPorts if oRole is not None for s in oRole.names()}


def same_value(oActual, oExpected):
    if oActual is None:
        return False
    return str(oActual).lower() == str(oExpected).lower()


class Library:
    """All declarations of a design: from library files, the design section, and for single instances."""

    def __init__(self):
        self.types = []
        self.instances = []

    def add_types(self, dTypes, sSource):
        if not isinstance(dTypes, dict):
            raise exceptions.ConfigurationError(f"ERROR: black_boxes in {sSource} maps component names to declarations")
        # Later sources take precedence: the design section over library files
        self.types = [Declaration(str(k), v, sSource) for k, v in dTypes.items()] + self.types

    def add_instances(self, dInstances, sSource):
        if not isinstance(dInstances, dict):
            raise exceptions.ConfigurationError(f"ERROR: black_box_instances in {sSource} maps instance paths to declarations")
        self.instances = [Declaration(str(k), v, sSource) for k, v in dInstances.items()] + self.instances

    def find(self, sType, sInstance):
        """Returns the declarations that apply to an instance: those of the instance first, then of its type."""
        lReturn = [o for o in self.instances if fnmatch.fnmatchcase(sInstance.lower(), o.name.lower())]
        lTypes = [o for o in self.types if o.name.lower() == sType.lower()]
        lTypes += [o for o in self.types if o not in lTypes and fnmatch.fnmatchcase(sType.lower(), o.name.lower())]
        return lReturn + lTypes[:1]


def from_design(dDesign):
    """Returns the Library of a design section: black_box_libraries, black_boxes and black_box_instances."""
    oLibrary = Library()
    for sFile in as_list(dDesign.get("black_box_libraries")):
        sFile = os.path.expandvars(sFile)
        try:
            with open(sFile, encoding="utf-8") as oFile:
                dFile = yaml.safe_load(oFile) or {}
        except (OSError, yaml.YAMLError) as e:
            raise exceptions.ConfigurationError(f"ERROR: could not read black box library {sFile}: {e}") from e
        oLibrary.add_types(dFile.get("black_boxes") or {}, sFile)
        oLibrary.add_instances(dFile.get("black_box_instances") or {}, sFile)
    oLibrary.add_types(dDesign.get("black_boxes") or {}, "design section")
    oLibrary.add_instances(dDesign.get("black_box_instances") or {}, "design section")
    return oLibrary


class Instance:
    """A black box instance of the flat netlist with the declarations that apply to it."""

    def __init__(self, oCell, lDeclarations):
        self.cell = oCell
        self.declarations = lDeclarations
        self.generics = generic_values(oCell)
        self._dRoles = {}

    def declared(self):
        return bool(self.declarations)

    def role(self, sPort):
        """The role of a port; None for a port without one."""
        if sPort not in self._dRoles:
            oRole = None
            for oDeclaration in self.declarations:
                bFound, oRole = oDeclaration.role(sPort, self.generics)
                if bFound:
                    break
            self._dRoles[sPort] = oRole
        return self._dRoles[sPort]

    def referenced(self, sPort):
        return any(sPort.lower() in o.referenced_ports(self.generics) for o in self.declarations)

    def reviewed_by(self, oRole=None):
        if oRole is not None and oRole.reviewed_by:
            return oRole.reviewed_by
        return next((o.reviewed_by for o in self.declarations if o.reviewed_by), "")

    def reference(self):
        return next((o.reference for o in self.declarations if o.reference), "")

    def stages(self, oRole):
        """The number of stages of a synchronized output: a number, or the value of a generic; None if not known."""
        if oRole.stages is None:
            return None
        if isinstance(oRole.stages, int):
            return oRole.stages
        oValue = self.generics.get(str(oRole.stages).lower())
        return oValue if isinstance(oValue, int) else None

    def problems(self, dPorts):
        """Returns the problems of the declaration for the ports of the instance, {port: direction}."""
        lReturn = []
        setPorts = {s.lower() for s in dPorts}
        for sPort in sorted(dPorts):
            oRole = self.role(sPort)
            if oRole is None and not self.referenced(sPort):
                lReturn.append(f"port {sPort} has no role")
            elif oRole is not None and oRole.kind == "static":
                if not oRole.justification:
                    lReturn.append(f"static port {sPort} needs a justification")
                if not self.reviewed_by(oRole):
                    lReturn.append(f"static port {sPort} needs reviewed_by")
        for oDeclaration in self.declarations:
            for _, oRole in oDeclaration.ports:
                for sName in oRole.names() if oRole is not None else []:
                    if sName.lower() not in setPorts:
                        lReturn.append(f"the declaration names port {sName}, which {self.cell.type} does not have")
            for sPattern, _ in oDeclaration.ports:
                if not any(c in sPattern for c in "*?[") and sPattern.lower() not in setPorts:
                    lReturn.append(f"the declaration names port {sPattern}, which {self.cell.type} does not have")
        return sorted(set(lReturn))


def generic_values(oCell):
    """Returns {generic name in lower case: value} of a cell: integers for binary values, else strings."""
    dReturn = {}
    for sName, oValue in (oCell.cell.get("parameters") or {}).items():
        sValue = str(oValue)
        if sValue and set(sValue) <= {"0", "1"}:
            iValue = int(sValue, 2)
            # A negative 32 bit integer
            dReturn[sName.lower()] = iValue - (1 << 32) if len(sValue) == 32 and sValue[0] == "1" else iValue
        else:
            dReturn[sName.lower()] = sValue.strip()
    return dReturn


def template(oFlat, oLibrary):
    """Returns a YAML template of declarations for the black box types of a flat netlist that have none."""
    dTypes = {}
    for oCell in oFlat.cells:
        if oCell.is_black_box():
            dTypes.setdefault(oCell.type, []).append(oCell)
    lLines = [
        f"# Black box declarations for {oFlat.top}, written by mhsg --black_box_template.",
        "# Give every port a role, or use an archetype, and fill in reference and reviewed_by;",
        "# see Black boxes in the design analysis documentation. Design analysis reports TODO as a missing role.",
        "",
    ]
    lMissing = [s for s in sorted(dTypes, key=str.lower) if not oLibrary.find(s, repr(dTypes[s][0]))]
    if not lMissing:
        lLines.append("# Every black box type of the design is declared.")
        lLines.append("black_boxes: {}")
        return "\n".join(lLines) + "\n"
    lLines.append("black_boxes:")
    for sType in lMissing:
        lCells = dTypes[sType]
        lLines.append(f"  {sType}:")
        sInstances = ", ".join(repr(o) for o in lCells[:5]) + (f", ... ({len(lCells)} in all)" if len(lCells) > 5 else "")
        lLines.append(f"    # Instances: {sInstances}")
        dGenerics = {}
        for oCell in lCells:
            for sName, oValue in generic_values(oCell).items():
                dGenerics.setdefault(sName, [])
                if oValue not in dGenerics[sName]:
                    dGenerics[sName].append(oValue)
        if dGenerics:
            lLines.append("    # Generics: " + "; ".join(f"{k} = {', '.join(map(str, v))}" for k, v in sorted(dGenerics.items())))
        lLines.append(f"    reference: {MISSING}")
        lLines.append(f"    reviewed_by: {MISSING}")
        lLines.append("    ports:")
        dPorts = port_list(oFlat, lCells[0])
        iWidth = max([len(s) for s in dPorts] + [1])
        for sPort, (sDirection, iBits) in dPorts.items():
            sBits = "1 bit" if iBits == 1 else f"{iBits} bits"
            lLines.append(f"      {(sPort + ':').ljust(iWidth + 1)} {MISSING}  # {sDirection}, {sBits}")
    return "\n".join(lLines) + "\n"


def port_list(oFlat, oCell):
    """Returns {port: (direction, bits)} of a black box, from its module in the netlist or its connections."""
    dModule = oFlat.netlist.black_boxes.get(oCell.type)
    if dModule:
        return {s: (d.get("direction", "input"), len(d.get("bits", []))) for s, d in dModule.get("ports", {}).items()}
    return {s: (oFlat.direction(oCell, s), len(l)) for s, l in oCell.connections.items()}


def is_variable(oBit):
    return graph.is_variable(oBit)
