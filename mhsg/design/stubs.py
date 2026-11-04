# -*- coding: utf-8 -*-
"""
Stub packages of vendor libraries, for analyzing a design without the vendor's installation.

A vendor library entry with stubs: true, such as {vendor: xilinx, stubs: true} or {library: unisim, stubs: true},
makes mhsg write the packages the design uses from that library, such as unisim.vcomponents, with a component
declaration for each vendor component the design instantiates. Each component gets the ports and generics its
instances name:

* the type of a port comes from the actual: the declared type of the signal or port, its element type for an
  indexed name, std_logic for a character literal, std_logic_vector for a string, bit string or aggregate;
* the mode of a port comes from Yosys' cell model of the primitive, for a black box library of the design that has
  models, such as xilinx; then from the black box declarations, see black_box.py, where a role says it; otherwise a
  port whose actual is an input of the entity, a signal the design assigns, an expression or a literal is an input,
  and any other port is an output, unless another output already drives its signal;
* the type of a generic comes from the actual: integer, real, boolean, string, time, bit_vector for a bit string,
  or the declared type of a constant or generic.

Array ports and generics are unconstrained, so each instance takes the width of its actual. The ports and generics
of a component that no instance names are not declared; neither are the components the design does not use. A stub
is not a vendor file: it says nothing about the primitive beyond what the design shows, which is all design analysis
needs of a black box.
"""

import ast
import os
import re

from mhsg import exceptions, parser, vhdlFile
from mhsg.design import verilog_black_boxes
from mhsg.lint import model

# Library -> name prefixes of its components, for a file that uses several stub libraries
PREFIXES = {"xpm": ("xpm_",)}
# Types a stub may use: std, ieee.std_logic_1164 and ieee.numeric_std
KNOWN_TYPES = (
    "std_logic",
    "std_ulogic",
    "std_logic_vector",
    "std_ulogic_vector",
    "unsigned",
    "signed",
    "bit",
    "bit_vector",
    "boolean",
    "integer",
    "natural",
    "positive",
    "real",
    "string",
    "time",
    "character",
)
# Array type -> element type, for an indexed name
ELEMENTS = {
    "std_logic_vector": "std_logic",
    "std_ulogic_vector": "std_ulogic",
    "unsigned": "std_logic",
    "signed": "std_logic",
    "bit_vector": "bit",
    "string": "character",
}
UNITS = ("fs", "ps", "ns", "us", "ms", "sec", "min", "hr")


class Instance:
    def __init__(self, sLabel, sUnit, iLine):
        self.label = sLabel
        self.unit = sUnit
        self.line = iLine
        # (formal, actual text, actual tokens) in order
        self.generics = []
        self.ports = []
        # Lower case name -> name as written
        self.spelling = {}


class SourceFile:
    """What a design file tells about the vendor components it instantiates."""

    def __init__(self, sFileName):
        self.name = sFileName
        self.uses = []
        self.components = set()
        self.entities = set()
        # Name -> (type mark, mode or None) of the ports, generics, signals and constants of the file
        self.objects = {}
        self.ports = {}
        self.targets = set()
        self.instances = []
        # Function name -> return type mark
        self.functions = {}
        # Subtype name -> (type mark, constraint)
        self.subtypes = {}
        # Record type -> {element: Object}
        self.records = {}
        # The integer values of constants and generics, see values
        self._dValues = None

    def read(self):
        lLines, eError = vhdlFile.utils.read_vhdlfile(self.name)
        if eError:
            raise exceptions.ConfigurationError(f"ERROR: stub libraries: cannot read {self.name}")
        self.scan(vhdlFile.vhdlFile(lLines))
        return self

    def scan(self, oFile):
        sLibrary = None
        sContext = None
        lNames = []
        sMode = None
        oInstance = None
        sMap = None
        iDepth = 0
        lFormal = []
        lActual = []
        # The rest of a declaration after its type mark: the constraint and the default value
        lTail = None
        tDeclaration = None
        sFunction = None
        bReturn = False
        sSubtype = None
        sTypeName = None
        sRecord = None
        for iToken, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            sValue = oToken.get_value()
            if tKind is None or not sValue.strip() or isinstance(oToken, parser.comment):
                continue
            if lTail is not None:
                if sValue == "(":
                    iDepth += 1
                elif sValue == ")":
                    iDepth -= 1
                if iDepth < 0 or (sValue == ";" and iDepth == 0):
                    self.declare(tDeclaration, lTail)
                    lTail = None
                    iDepth = 0
                else:
                    lTail.append(sValue)
                    continue
            if tKind == ("full_type_declaration", "identifier"):
                sTypeName = sValue.lower()
            elif tKind == ("record_type_definition", "record_keyword"):
                sRecord = sTypeName
                self.records.setdefault(sRecord, {})
            elif tKind == ("record_type_definition", "end_keyword"):
                sRecord = None
            elif sRecord and tKind == ("identifier_list", "identifier"):
                lNames.append(sValue.lower())
            elif tKind == ("subtype_declaration", "identifier"):
                sSubtype = sValue.lower()
            elif sSubtype and tKind == ("type_mark", "name") and sSubtype not in self.subtypes:
                self.subtypes[sSubtype] = [sValue.lower(), ""]
            elif sSubtype and tKind == ("subtype_declaration", "semicolon"):
                sSubtype = None
            elif sSubtype and sSubtype in self.subtypes:
                self.subtypes[sSubtype][1] += " " + sValue.lower()
            elif tKind == ("function_specification", "designator"):
                sFunction = sValue.lower()
            elif tKind == ("function_specification", "return_keyword"):
                bReturn = True
            elif bReturn and tKind == ("type_mark", "name"):
                self.functions[sFunction] = sValue.lower()
                bReturn = False
            elif tKind == ("use_clause", "library_name"):
                sLibrary = sValue.lower()
            elif tKind == ("use_clause", "package_name") and sLibrary:
                self.uses.append((sLibrary, sValue.lower()))
                sLibrary = None
            elif tKind == ("entity_declaration", "entity_keyword"):
                sContext = "entity"
            elif tKind == ("entity_declaration", "identifier"):
                self.entities.add(sValue.lower())
            elif tKind == ("entity_declaration", "semicolon"):
                sContext = None
            elif tKind == ("component_declaration", "component_keyword"):
                sContext = "component"
            elif tKind == ("component_declaration", "identifier"):
                self.components.add(sValue.lower())
            elif tKind == ("component_declaration", "semicolon"):
                sContext = None
            elif tKind[1] == "identifier" and tKind[0] in ("signal_declaration", "constant_declaration", "interface_unknown_declaration"):
                if tKind[0] != "interface_unknown_declaration" or sContext == "entity":
                    lNames.append(sValue.lower())
            elif tKind[0] == "mode" and lNames:
                sMode = sValue.lower()
            elif tKind == ("type_mark", "name") and lNames:
                tDeclaration = (lNames, sValue.lower(), sMode, sRecord)
                lTail = []
                iDepth = 0
                lNames = []
                sMode = None
            elif tKind[1] == "target":
                self.targets.add(base_name(sValue))
            elif tKind == ("component_instantiation_statement", "instantiation_label"):
                oInstance = Instance(sValue.lower(), None, oFile.oTokenMap.get_line_number_of_index(iToken))
            elif oInstance is not None and tKind == ("instantiated_unit", "component_name"):
                oInstance.unit = sValue.lower()
                oInstance.spelling[sValue.lower().split(".")[-1]] = sValue.split(".")[-1]
            elif oInstance is not None and tKind[0] == "instantiated_unit":
                # An entity or configuration: not a vendor component
                oInstance = None
            elif oInstance is not None and tKind in (("generic_map_aspect", "open_parenthesis"), ("port_map_aspect", "open_parenthesis")):
                sMap = tKind[0]
                iDepth, lFormal, lActual = 0, [], []
            elif oInstance is not None and sMap and tKind == (sMap, "close_parenthesis"):
                self.associate(oInstance, sMap, lFormal, lActual)
                sMap = None
            elif oInstance is not None and sMap:
                if tKind == ("association_list", "comma") and iDepth == 0:
                    self.associate(oInstance, sMap, lFormal, lActual)
                    lFormal, lActual = [], []
                    continue
                if sValue == "(":
                    iDepth += 1
                elif sValue == ")":
                    iDepth -= 1
                if tKind == ("association_element", "formal_part"):
                    lFormal.append(oToken)
                elif tKind != ("association_element", "assignment") or iDepth > 0:
                    lActual.append(oToken)
            elif oInstance is not None and tKind == ("component_instantiation_statement", "semicolon"):
                if oInstance.unit:
                    self.instances.append(oInstance)
                oInstance = None

    def declare(self, tDeclaration, lTail):
        lNames, sType, sMode, sRecord = tDeclaration
        sTail = " ".join(lTail).lower()
        sConstraint, _, sDefault = sTail.partition(":=")
        for sName in lNames:
            if sRecord:
                self.records[sRecord][sName] = Object(sType, None, sConstraint.strip(), "")
                continue
            self.objects[sName] = Object(sType, sMode, sConstraint.strip(), sDefault.strip())
            if sMode is not None:
                self.ports[sName] = sMode

    def values(self, dGenerics):
        """{name: integer value} of the constants and generics with integer values, the design's generics first."""
        if self._dValues is not None:
            return self._dValues
        dReturn = {}
        for _ in range(3):
            for sName, oObject in self.objects.items():
                if oObject.default and sName not in dReturn and (oObject.mode is None or sName in dGenerics):
                    iValue = evaluate(oObject.default, dReturn)
                    if iValue is not None:
                        dReturn[sName] = iValue
        dReturn.update({k.lower(): v for k, v in dGenerics.items() if isinstance(v, int) and not isinstance(v, bool)})
        self._dValues = dReturn
        return dReturn

    def associate(self, oInstance, sMap, lFormal, lActual):
        if not lFormal and not lActual:
            return
        if not lFormal:
            raise exceptions.ConfigurationError(
                f"ERROR: stub libraries: instance {oInstance.label} of {oInstance.unit} in {self.name}({oInstance.line}) associates by position; name the "
                "ports and generics so a stub can declare them",
            )
        sFormal = lFormal[0].get_value().lower()
        oInstance.spelling.setdefault(sFormal, lFormal[0].get_value())
        sActual = " ".join(o.get_value() for o in lActual).lower()
        (oInstance.generics if sMap == "generic_map_aspect" else oInstance.ports).append((sFormal, sActual, lActual))


class Object:
    """A port, generic, signal or constant: its type mark, mode (None but for ports), constraint and default value."""

    def __init__(self, sType, sMode, sConstraint, sDefault):
        self.type = sType
        self.mode = sMode
        self.constraint = sConstraint
        self.default = sDefault


def evaluate(sExpression, dValues):
    """The value of an integer expression of literals and named values, or None."""
    try:
        oTree = ast.parse(sExpression.strip().lower(), mode="eval")
    except SyntaxError:
        return None

    def value(oNode):
        if isinstance(oNode, ast.Expression):
            return value(oNode.body)
        if isinstance(oNode, ast.Constant) and isinstance(oNode.value, int) and not isinstance(oNode.value, bool):
            return oNode.value
        if isinstance(oNode, ast.Name):
            return dValues[oNode.id]
        if isinstance(oNode, ast.UnaryOp) and isinstance(oNode.op, (ast.USub, ast.UAdd)):
            return -value(oNode.operand) if isinstance(oNode.op, ast.USub) else value(oNode.operand)
        if isinstance(oNode, ast.BinOp) and isinstance(oNode.op, (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Div)):
            iLeft, iRight = value(oNode.left), value(oNode.right)
            if isinstance(oNode.op, ast.Add):
                return iLeft + iRight
            if isinstance(oNode.op, ast.Sub):
                return iLeft - iRight
            if isinstance(oNode.op, ast.Mult):
                return iLeft * iRight
            return iLeft // iRight
        raise KeyError(oNode)

    try:
        return value(oTree)
    except (KeyError, ZeroDivisionError, RecursionError):
        return None


def range_width(sRange, dValues):
    """The number of elements of a range such as 7 downto 0, or None."""
    oMatch = re.fullmatch(r"\(?(.+?)\s+(downto|to)\s+(.+?)\)?", sRange.strip())
    if oMatch is None:
        return None
    iLeft = evaluate(oMatch.group(1), dValues)
    iRight = evaluate(oMatch.group(3), dValues)
    if iLeft is None or iRight is None:
        return None
    return max(0, iLeft - iRight + 1 if oMatch.group(2) == "downto" else iRight - iLeft + 1)


def base_name(sName):
    return re.split(r"[(.\s]", sName.strip().lower(), maxsplit=1)[0]


class Component:
    def __init__(self, sName):
        # In lower case; spelling holds the names as the design first writes them
        self.name = sName
        self.spelling = {}
        self.instances = 0
        # Name -> list of (file, actual text, actual tokens), in order of appearance
        self.ports = {}
        self.generics = {}


def libraries(oDesign):
    """The stub libraries of a design: {library name: vendor}."""
    return {o.name.lower(): o.vendor for o in oDesign.vendor_libraries if getattr(o, "stubs", False)}


def owner(sUnit, oSource, dLibraries):
    """The (library, package) a component instance comes from, or None if it is not a stub library's."""
    lParts = sUnit.split(".")
    if len(lParts) == 3:
        return (lParts[0], lParts[1]) if lParts[0] in dLibraries else None
    lCandidates = [t for t in oSource.uses if t[0] in dLibraries]
    if not lCandidates:
        return None
    for tCandidate in lCandidates:
        if any(sUnit.startswith(s) for s in PREFIXES.get(tCandidate[0], ())):
            return tCandidate
    lPlain = [t for t in lCandidates if t[0] not in PREFIXES]
    return (lPlain or lCandidates)[0]


def collect(oDesign, lSources):
    """Returns {(library, package): {component name: Component}} for the stub libraries of a design."""
    dLibraries = libraries(oDesign)
    setDefined = set()
    for oSource in lSources:
        setDefined |= oSource.entities | oSource.components
    dReturn = {}
    for oSource in lSources:
        for tPackage in oSource.uses:
            if tPackage[0] in dLibraries:
                dReturn.setdefault(tPackage, {})
        for oInstance in oSource.instances:
            sName = oInstance.unit.split(".")[-1]
            if sName in setDefined:
                continue
            tPackage = owner(oInstance.unit, oSource, dLibraries)
            if tPackage is None:
                continue
            oComponent = dReturn.setdefault(tPackage, {}).setdefault(sName, Component(sName))
            oComponent.instances += 1
            for sKey, sSpelling in oInstance.spelling.items():
                oComponent.spelling.setdefault(sKey, sSpelling)
            for sFormal, sActual, lActual in oInstance.generics:
                oComponent.generics.setdefault(sFormal, []).append((oSource, sActual, lActual))
            for sFormal, sActual, lActual in oInstance.ports:
                oComponent.ports.setdefault(sFormal, []).append((oSource, sActual, lActual))
    return dReturn


# The subtypes of the design, {name: [type mark, constraint]}, and its record types, {name: {element: Object}}, for
# the stubs being written
SUBTYPES = {}
RECORDS = {}

reSelected = re.compile(r"([a-z]\w*)((?:\s*\.\s*[a-z]\w*)*)\s*(.*)", re.DOTALL)


def selected(sActual, oSource):
    """(Object, rest) of the signal, port or record element an actual names, such as r.read(3), or (None, None)."""
    oMatch = reSelected.fullmatch(sActual.strip())
    if oMatch is None or oMatch.group(1) not in oSource.objects:
        return None, None
    oObject = oSource.objects[oMatch.group(1)]
    for sElement in [s.strip() for s in oMatch.group(2).split(".") if s.strip()]:
        dElements = RECORDS.get(resolve(oObject.type)[0])
        if dElements is None or sElement not in dElements:
            return None, None
        oObject = dElements[sElement]
    return oObject, oMatch.group(3).strip()


def resolve(sType):
    """(base type, constraint) of a type mark, following the subtypes of the design to a type a stub can declare."""
    sConstraint = ""
    for _ in range(16):
        if sType in KNOWN_TYPES or sType not in SUBTYPES:
            break
        sType, sOwn = SUBTYPES[sType]
        sConstraint = sConstraint or sOwn.strip()
    return sType, sConstraint


def literal_type(sActual, lActual, bGeneric):
    """The type of a literal or aggregate actual, or None if the actual is not one."""
    if lActual and model.kind(lActual[0]) == ("bit_string_literal", "base_specifier"):
        return "bit_vector" if bGeneric else "std_logic_vector"
    if sActual.startswith("'"):
        return "std_ulogic" if bGeneric else "std_logic"
    if sActual.startswith('"'):
        return "string" if bGeneric else "std_logic_vector"
    if sActual.startswith("("):
        return "std_logic_vector"
    if re.fullmatch(r"[+-]?\s*\d[\d_]*", sActual):
        return "integer"
    if re.fullmatch(r"[+-]?\s*\d[\d_]*\.\d[\d_]*(e[+-]?\d+)?", sActual):
        return "real"
    if sActual in ("true", "false"):
        return "boolean"
    if re.fullmatch(r"[\d_.]+\s*(" + "|".join(UNITS) + r")", sActual):
        return "time"
    return None


def name_type(sActual, oSource):
    """The type of an actual that is a name, a slice, an indexed name or a type conversion, or None."""
    sBase = base_name(sActual)
    sRest = sActual.strip()[len(sBase) :].strip()
    if sBase in KNOWN_TYPES and sRest.startswith("("):
        return sBase
    if sBase in oSource.functions:
        return resolve(oSource.functions[sBase])[0]
    oObject, sRest = selected(sActual, oSource)
    if oObject is None:
        return None
    sType = resolve(oObject.type)[0]
    if not sRest:
        return sType
    if sRest.startswith("(") and not re.search(r"\b(downto|to)\b", sRest):
        return ELEMENTS.get(sType, sType)
    return sType


def actual_width(sActual, lActual, oSource, dGenerics):
    """The number of elements of an array actual, or None if it is not known."""
    if lActual and model.kind(lActual[0]) == ("bit_string_literal", "base_specifier") and len(lActual) > 1:
        sBase = lActual[0].get_value().lower()
        sDigits = lActual[1].get_value().strip('"').replace("_", "")
        oPrefix = re.match(r"\d+", sBase)
        if oPrefix:
            return int(oPrefix.group(0))
        return len(sDigits) * {"b": 1, "o": 3, "x": 4}.get(sBase[-1:], 1)
    if sActual.startswith('"'):
        return len(sActual.strip('"'))
    sBase = base_name(sActual)
    sRest = sActual.strip()[len(sBase) :].strip()
    if sBase in KNOWN_TYPES and sRest.startswith("(") and sRest.endswith(")"):
        return actual_width(sRest[1:-1].strip(), lActual[2:-1], oSource, dGenerics)
    oObject, sRest = selected(sActual, oSource)
    if oObject is None:
        return None
    dValues = oSource.values(dGenerics)
    if not sRest:
        sConstraint = oObject.constraint or resolve(oObject.type)[1]
        return range_width(sConstraint, dValues) if sConstraint else None
    if re.search(r"\b(downto|to)\b", sRest):
        return range_width(sRest, dValues)
    return None


def port_type(oComponent, sPort, dGenerics=None):
    """The type of a port; an array type is constrained when its instances agree on the width."""
    sReturn = "std_logic"
    for oSource, sActual, lActual in oComponent.ports[sPort]:
        if sActual == "open":
            continue
        sType = literal_type(sActual, lActual, False) or name_type(sActual, oSource)
        if sType is not None:
            sReturn = sType
            break
    if sReturn not in ELEMENTS:
        return sReturn
    setWidths = {actual_width(sActual, lActual, oSource, dGenerics or {}) for oSource, sActual, lActual in oComponent.ports[sPort] if sActual != "open"}
    setWidths.discard(None)
    if len(setWidths) == 1:
        return f"{sReturn}({setWidths.pop() - 1} downto 0)"
    if not setWidths and any(sActual == "open" or sActual.startswith("(") for _, sActual, _ in oComponent.ports[sPort]):
        # An aggregate or an open port needs a width, which no instance gives: one element is enough for analysis
        return f"{sReturn}(0 downto 0)"
    return sReturn


# The value a generic takes when an instance leaves it out
TYPE_DEFAULTS = {
    "integer": "0",
    "natural": "0",
    "positive": "1",
    "real": "0.0",
    "boolean": "false",
    "string": '""',
    "time": "0 ns",
    "bit_vector": '"0"',
    "std_ulogic": "'0'",
    "std_logic": "'0'",
    "bit": "'0'",
    "character": "' '",
}


def generic_default(oComponent, sGeneric, sType, dGenerics):
    """A default for a generic some instances leave out: the first literal actual, or a value of its type."""
    for oSource, sActual, lActual in oComponent.generics[sGeneric]:
        if literal_type(sActual, lActual, True) is not None:
            return "".join(o.get_value() for o in lActual) if model.kind(lActual[0])[0] == "bit_string_literal" else " ".join(o.get_value() for o in lActual)
        iValue = oSource.values(dGenerics).get(base_name(sActual))
        if iValue is not None and sActual == base_name(sActual):
            return str(iValue)
    return TYPE_DEFAULTS.get(sType, "0")


def generic_type(oComponent, sGeneric):
    for oSource, sActual, lActual in oComponent.generics[sGeneric]:
        sType = literal_type(sActual, lActual, True) or name_type(sActual, oSource)
        if sType is not None:
            return sType
    return "integer"


def port_modes(oDesign, dComponents, lSources, sDataDirectory=None):
    """
    Returns {(component, port): in | out | inout}: from Yosys' cell model of the primitive, for the black box libraries
    of the design that have models, then from the roles of its declaration, then from the design.
    """
    dModels = {}
    if sDataDirectory:
        lFiles = [s for sLibrary in oDesign.black_box_libraries for s in verilog_black_boxes.YOSYS_MODELS.get(sLibrary, [])]
        dFound = verilog_black_boxes.model_directions(sDataDirectory, lFiles, {o.name for o in dComponents.values()})
        dModels = {k.lower(): {p.lower(): d for p, d in v.items()} for k, v in dFound.items()}
    dReturn = {}
    setDriven = set()
    for oSource in lSources:
        setDriven |= {(oSource.name, s) for s in oSource.targets}
        setDriven |= {(oSource.name, s) for s, sMode in oSource.ports.items() if sMode in ("in", "inout")}
    lUnknown = []
    for oComponent in dComponents.values():
        dDeclared = verilog_black_boxes.directions(oDesign, oComponent.name, list(oComponent.ports))
        dModel = dModels.get(oComponent.name, {})
        for sPort, lActuals in oComponent.ports.items():
            sDirection = dModel.get(sPort) or dDeclared.get(sPort)
            if sDirection in ("input", "output") or (sDirection == "inout" and sPort in dModel):
                dReturn[(oComponent.name, sPort)] = {"input": "in", "output": "out", "inout": "inout"}[sDirection]
            else:
                lUnknown.append((oComponent, sPort, lActuals))
    # Signals the declared outputs drive
    for oComponent in dComponents.values():
        for sPort, lActuals in oComponent.ports.items():
            if dReturn.get((oComponent.name, sPort)) == "out":
                setDriven |= {(oSource.name, base_name(sActual)) for oSource, sActual, _ in lActuals}
    for oComponent, sPort, lActuals in lUnknown:
        sMode = None
        for oSource, sActual, lActual in lActuals:
            if sActual == "open":
                continue
            sBase = base_name(sActual)
            if literal_type(sActual, lActual, False) is not None or not re.fullmatch(r"[a-z]\w*", sBase) or sBase in KNOWN_TYPES:
                sMode = "in"
            elif oSource.ports.get(sBase) in ("out", "buffer"):
                sMode = "out"
            elif (oSource.name, sBase) in setDriven:
                sMode = "in"
            if sMode is not None:
                break
        if sMode is None:
            sMode = "out"
            setDriven |= {(oSource.name, base_name(sActual)) for oSource, sActual, _ in lActuals}
        dReturn[(oComponent.name, sPort)] = sMode
    return dReturn


def declarable(sType, sFallback):
    """(type, comment): a type a stub can declare, or the fallback with a comment naming the type it stands for."""
    sBase = sType.split("(")[0].strip()
    if sBase in KNOWN_TYPES:
        return sType, ""
    return sFallback, f"  -- {sBase} cannot be declared here"


def lines(lItems):
    """The lines of an interface list of (declaration, comment): a semicolon after each declaration but the last."""
    return [f"      {s}{';' if i < len(lItems) - 1 else ''}{sNote}" for i, (s, sNote) in enumerate(lItems)]


def package_text(sLibrary, sPackage, dComponents, dModes, dGenerics=None):
    lLines = [
        f"-- Stub package {sLibrary}.{sPackage}, written by mhsg from the instances of the design, see stubs.py",
        "library ieee;",
        "use ieee.std_logic_1164.all;",
        "use ieee.numeric_std.all;",
        "",
        f"package {sPackage} is",
    ]
    for sName in sorted(dComponents):
        oComponent = dComponents[sName]
        lLines.append(f"  component {oComponent.spelling.get(sName, sName)} is")
        lGenerics = []
        for sGeneric in oComponent.generics:
            sType, sNote = declarable(generic_type(oComponent, sGeneric), "integer")
            sDefault = ""
            if len(oComponent.generics[sGeneric]) < oComponent.instances:
                sDefault = " := " + generic_default(oComponent, sGeneric, sType, dGenerics or {})
            lGenerics.append((f"{oComponent.spelling.get(sGeneric, sGeneric)} : {sType}{sDefault}", sNote))
        if lGenerics:
            lLines.append("    generic (")
            lLines += lines(lGenerics)
            lLines.append("    );")
        lPorts = []
        for sPort, lActuals in oComponent.ports.items():
            sType, sNote = declarable(port_type(oComponent, sPort, dGenerics), "std_logic")
            sMode = dModes[(sName, sPort)]
            sDefault = ""
            if sMode == "in" and any(s == "open" for _, s, _ in lActuals):
                sDefault = " := '0'" if sType in ("std_logic", "std_ulogic") else " := (others => '0')" if "(" in sType else ""
            lPorts.append((f"{oComponent.spelling.get(sPort, sPort)} : {sMode} {sType}{sDefault}", sNote))
        if lPorts:
            lLines.append("    port (")
            lLines += lines(lPorts)
            lLines.append("    );")
        lLines.append("  end component;")
    lLines.append(f"end package {sPackage};")
    return "\n".join(lLines) + "\n"


def write(oDesign, sWorkDirectory, sDataDirectory=None):
    """
    Writes the stub packages of the design's stub libraries into the work directory and makes them the files of those
    libraries. sDataDirectory is Yosys' data directory, whose cell models give the directions of the ports. Returns
    {library: [files]}.
    """
    dLibraries = libraries(oDesign)
    if not dLibraries:
        return {}
    lSources = [SourceFile(s).read() for s in oDesign.vhdl_files()]
    SUBTYPES.clear()
    RECORDS.clear()
    for oSource in lSources:
        for sName, lSubtype in oSource.subtypes.items():
            SUBTYPES.setdefault(sName, lSubtype)
        for sName, dElements in oSource.records.items():
            RECORDS.setdefault(sName, dElements)
    dPackages = collect(oDesign, lSources)
    dComponents = {}
    for dPackage in dPackages.values():
        dComponents.update(dPackage)
    dModes = port_modes(oDesign, dComponents, lSources, sDataDirectory)
    sDirectory = os.path.join(sWorkDirectory, "stubs")
    os.makedirs(sDirectory, exist_ok=True)
    dReturn = {}
    for (sLibrary, sPackage), dPackage in sorted(dPackages.items()):
        sFile = os.path.join(sDirectory, f"{sLibrary}.{sPackage}.vhd")
        with open(sFile, "w", encoding="utf-8") as oFile:
            oFile.write(package_text(sLibrary, sPackage, dPackage, dModes, oDesign.generics))
        dReturn.setdefault(sLibrary, []).append(sFile)
    for oLibrary in oDesign.libraries:
        if oLibrary.name.lower() in dLibraries:
            oLibrary.files[:] = dReturn.get(oLibrary.name.lower(), [])
    return dReturn
