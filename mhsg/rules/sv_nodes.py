# -*- coding: utf-8 -*-
"""Helpers for the SystemVerilog rules that look at the syntax tree: parents, literals and declared names."""

import os

from mhsg import language, parser
from mhsg.rules.sv_tree import Problem, descendants, elements
from mhsg.svFile import tokens

# Kinds of syntax nodes holding a data type whose dimensions are packed
PACKED_TYPES = ("LogicType", "BitType", "RegType", "ImplicitType", "IntegerType", "NamedType", "TimeType")


def ancestors(oNode):
    """The parents of a syntax node, nearest first."""
    oParent = oNode.parent
    while oParent is not None:
        yield oParent
        oParent = oParent.parent


def inside(oNode, *lKinds):
    """True if a syntax node is under a node of one of the kinds."""
    return any(o.kind.name in lKinds for o in ancestors(oNode))


def is_verilog(oFile):
    """True for a Verilog file, read as Verilog-2005: the rules give it advice without SystemVerilog constructs."""
    return getattr(oFile, "language", None) == language.VERILOG


def is_combinational(oBlock):
    """
    True for an always block of combinational logic as Verilog writes it: always @* or @(*), or an event control
    whose events have no edge, such as always @(a or b).
    """
    oStatement = oBlock.statement
    if oBlock.kind.name != "AlwaysBlock" or oStatement is None or oStatement.kind.name != "TimingControlStatement":
        return False
    oControl = oStatement.timingControl
    if oControl.kind.name == "ImplicitEventControl":
        return True
    if oControl.kind.name != "EventControlWithExpression":
        return False
    lEvents = [o for o in descendants(oControl) if o.kind.name == "SignalEventExpression"]
    return bool(lEvents) and not any(text(o.edge) for o in lEvents)


def combinational_blocks(oFile):
    """
    The always_comb blocks of a file; in a Verilog file, which has none, its combinational always blocks, see
    is_combinational.
    """
    if is_verilog(oFile):
        return [o for o in oFile.nodes("AlwaysBlock") if is_combinational(o)]
    return oFile.nodes("AlwaysCombBlock")


def text(oToken):
    return oToken.rawText if oToken is not None else ""


def integer_of(oNode):
    """The value of a literal expression without x or z digits, such as 8, 4'b0011 or 'hFF, or None."""
    sKind = oNode.kind.name
    if sKind == "IntegerLiteralExpression":
        try:
            return int(text(oNode.literal).replace("_", ""))
        except ValueError:
            return None
    if sKind == "IntegerVectorExpression":
        oLiteral = vector_literal(oNode)
        return oLiteral.value if oLiteral is not None else None
    return None


class VectorLiteral:
    """A based literal such as 4'b0011: its width (None if unsized), base letter, digits and value (None with x or z)."""

    def __init__(self, oNode):
        self.size = int(text(oNode.size).replace("_", "")) if oNode.size is not None and text(oNode.size) else None
        sBase = text(oNode.base).lower().replace("'", "").replace("s", "")
        self.base = sBase[:1]
        self.digits = text(oNode.value).replace("_", "")
        iRadix = {"b": 2, "o": 8, "d": 10, "h": 16}.get(self.base)
        try:
            self.value = int(self.digits, iRadix) if iRadix is not None else None
        except ValueError:
            self.value = None

    def bits(self):
        """The number of bits the digits need: one per binary digit, three per octal and four per hexadecimal digit."""
        if self.value is None:
            return None
        if self.base == "d":
            return max(self.value.bit_length(), 1)
        return max(self.value.bit_length(), 1)


def vector_literal(oNode):
    try:
        return VectorLiteral(oNode)
    except ValueError:
        return None


def has_x_or_z(oNode):
    """True for a literal with x, z or ? digits, such as 1'bx or 'z."""
    sKind = oNode.kind.name
    if sKind == "IntegerVectorExpression":
        return any(c in text(oNode.value).lower() for c in "xz?")
    if sKind == "UnbasedUnsizedLiteralExpression":
        return text(oNode.literal).lower() in ("'x", "'z")
    return False


def declared_names(oFile):
    """
    Yields (kind, syntax token) for each name the file declares, where kind is module, interface, package, program,
    instance, signal, port, parameter, localparam, macro, function, task, type, constraint or genvar.
    """
    for sKind, sCategory in (
        ("ModuleDeclaration", "module"),
        ("InterfaceDeclaration", "interface"),
        ("PackageDeclaration", "package"),
        ("ProgramDeclaration", "program"),
    ):
        for oNode in oFile.nodes(sKind):
            yield sCategory, oNode.header.name
    for oNode in oFile.nodes("HierarchicalInstance"):
        if oNode.decl is not None:
            yield "instance", oNode.decl.name
    for oNode in oFile.nodes("DataDeclaration", "NetDeclaration"):
        for oDeclarator in elements(oNode.declarators):
            yield "signal", oDeclarator.name
    for oNode in oFile.nodes("ImplicitAnsiPort", "FunctionPort"):
        if oNode.declarator is not None:
            yield "port", oNode.declarator.name
    for oNode in oFile.nodes("PortDeclaration"):
        for oDeclarator in elements(oNode.declarators):
            yield "port", oDeclarator.name
    for oNode in oFile.nodes("ParameterDeclaration"):
        sCategory = "localparam" if text(oNode.keyword) == "localparam" else "parameter"
        for oDeclarator in elements(oNode.declarators):
            yield sCategory, oDeclarator.name
    for oNode in oFile.nodes("DefineDirective"):
        yield "macro", oNode.name
    for oNode in oFile.nodes("FunctionPrototype"):
        sCategory = "task" if text(oNode.keyword) == "task" else "function"
        oName = oNode.name.getLastToken() if oNode.name is not None else None
        if oName is not None:
            yield sCategory, oName
    for oNode in oFile.nodes("TypedefDeclaration"):
        yield "type", oNode.name
    for oNode in oFile.nodes("ConstraintDeclaration"):
        oName = oNode.name.getLastToken() if oNode.name is not None else None
        if oName is not None:
            yield "constraint", oName
    for oNode in oFile.nodes("GenvarDeclaration"):
        for oIdentifier in elements(oNode.identifiers):
            yield "genvar", oIdentifier.identifier


def all_descendants(oNode):
    return list(descendants(oNode))


def names_of_kinds(oFile, lKinds):
    """The declared names of the given kinds, see declared_names."""
    return [(sKind, oName) for sKind, oName in declared_names(oFile) if sKind in lKinds]


def file_stem(sFileName):
    """The name of a file without its directory and extension: fifo for rtl/fifo.sv."""
    return os.path.splitext(os.path.basename(sFileName))[0]


def missing_lifetime(oFile, sKeyword, sSolution):
    """Yields Problems for the functions or tasks outside classes declared without automatic or static."""
    for oPrototype in oFile.nodes("FunctionPrototype"):
        # A missing token is an empty one
        if text(oPrototype.keyword) != sKeyword or text(oPrototype.lifetime):
            continue
        if inside(oPrototype, "ClassDeclaration") or inside(oPrototype, "ExternFuncDecl", "ModportSubroutinePort", "DPIImport"):
            continue
        oToken = oFile.token_at(oPrototype.keyword)
        if oToken is not None:
            yield Problem(oToken, sSolution)


def add_automatic(oViolation):
    """The fix of missing_lifetime: automatic after the function or task keyword."""
    oKeyword = oViolation.get_tokens()[0]
    oViolation.set_tokens([oKeyword, parser.whitespace(" "), tokens.keyword("automatic", "AutomaticKeyword")])


def anonymous_types(oFile, lKinds, sSolution):
    """Yields Problems for the types of the kinds declared outside a typedef, such as enum logic {A, B} state."""
    for oType in oFile.nodes(*lKinds):
        if inside(oType, "TypedefDeclaration", "TypeParameterDeclaration", "TypeAssignment"):
            continue
        oToken = oFile.token_at(oType.getFirstToken())
        if oToken is not None:
            yield Problem(oToken, sSolution)


# Reserved words of VHDL (IEEE 1076-2019), which the STARC guide keeps out of Verilog names
VHDL_KEYWORDS = set(
    """abs access after alias all and architecture array assert assume attribute begin block body buffer bus case
    component configuration constant context cover default disconnect downto else elsif end entity exit fairness file
    for force function generate generic group guarded if impure in inertial inout is label library linkage literal
    loop map mod nand new next nor not null of on open or others out package parameter port postponed private
    procedure process property protected pure range record register reject release rem report restrict return rol ror
    select sequence severity shared signal sla sll sra srl strong subtype then to transport type unaffected units
    until use variable view vmode vpkg vprop vunit wait when while with xnor xor""".split(),
)


def source(oNode):
    """The text of a syntax node as written, without the white space and comments before it."""
    sText = str(oNode)
    oFirst = oNode.getFirstToken()
    if oFirst is not None:
        sRest = sText[sum(len(o.getRawText()) for o in oFirst.trivia) :]
        if sRest.startswith(oFirst.rawText):
            return sRest.strip()
    lLines = sText.strip().splitlines()
    while lLines and lLines[0].strip().startswith("//"):
        lLines.pop(0)
    return "\n".join(lLines).strip()
