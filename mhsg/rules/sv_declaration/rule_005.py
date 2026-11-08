# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

# Members of a module that declare names in its scope, by kind
OUTER = {
    "DataDeclaration": "signal",
    "NetDeclaration": "signal",
    "PortDeclaration": "port",
    "ParameterDeclarationStatement": "parameter",
    "TypedefDeclaration": "type",
    "HierarchyInstantiation": "instance",
    "FunctionDeclaration": "function",
    "TaskDeclaration": "task",
    "GenvarDeclaration": "genvar",
}
BLOCKS = ("SequentialBlockStatement", "ParallelBlockStatement", "GenerateBlock")


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks that names are not used twice in a module: a variable declared in a block, function or generate
    block, a loop variable or a block label with the name of a port, signal, parameter, type, instance, function or
    task of the module. It is disabled by default; the do254 rule set enables it (DR3).

    A variable with the name of a signal hides the signal in its block, so a reader cannot tell which one a statement
    uses; a label with the name of a signal makes messages and waveforms ambiguous. The ports of functions and tasks
    are not checked.

    **Violation**

    .. code-block:: systemverilog

       logic [3:0] count;

       always_comb begin
           int count;

    **Fix**

    .. code-block:: systemverilog

       logic [3:0] count;

       always_comb begin
           int count_v;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Give the name to one declaration of the module"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration", "InterfaceDeclaration", "ProgramDeclaration"):
            dOuter = outer_names(oModule)
            for oName in inner_names(oModule):
                sName = text(oName)
                if sName in dOuter:
                    oToken = oFile.token_at(oName)
                    if oToken is not None:
                        yield Problem(oToken, f"Rename {sName}: the module declares a {dOuter[sName]} {sName} too")


def outer_names(oModule):
    """The names the module declares in its own scope: name -> kind."""
    dReturn = {}
    oHeader = oModule.header
    for oNode in descendants(oHeader):
        if oNode.kind.name in ("ImplicitAnsiPort",) and oNode.declarator is not None:
            dReturn.setdefault(text(oNode.declarator.name), "port")
        elif oNode.kind.name == "ParameterDeclaration":
            for oDeclarator in elements(oNode.declarators):
                dReturn.setdefault(text(oDeclarator.name), "parameter")
    for oMember in module_members(oModule):
        sKind = OUTER.get(oMember.kind.name)
        if sKind is None:
            continue
        for oName in member_names(oMember):
            dReturn.setdefault(text(oName), sKind)
    return dReturn


def member_names(oMember):
    """The name tokens a member of a module declares."""
    sKind = oMember.kind.name
    if sKind in ("DataDeclaration", "NetDeclaration", "PortDeclaration"):
        return [o.name for o in elements(oMember.declarators)]
    if sKind == "ParameterDeclarationStatement":
        return [o.name for oNode in descendants(oMember) if oNode.kind.name == "ParameterDeclaration" for o in elements(oNode.declarators)]
    if sKind == "TypedefDeclaration":
        return [oMember.name]
    if sKind == "HierarchyInstantiation":
        return [o.decl.name for o in elements(oMember.instances) if getattr(o, "decl", None) is not None]
    if sKind in ("FunctionDeclaration", "TaskDeclaration"):
        oName = oMember.prototype.name
        return [oName.getLastToken()] if oName is not None else []
    if sKind == "GenvarDeclaration":
        return [o.identifier for o in elements(oMember.identifiers)]
    return []


def module_members(oModule):
    """The members of a module, with those of its generate regions, which declare names in the module's scope."""
    lReturn = []
    for oMember in oModule.members:
        if oMember.kind.name == "GenerateRegion":
            lReturn.extend(o for o in oMember.members if hasattr(o, "kind"))
        else:
            lReturn.append(oMember)
    return lReturn


def inner_names(oModule):
    """The name tokens declared inside the blocks, functions and generate constructs of a module, in order."""
    lReturn = []
    for oMember in module_members(oModule):
        for oNode in [oMember, *descendants(oMember)]:
            sKind = oNode.kind.name
            if sKind == "DataDeclaration" and oNode is not oMember:
                lReturn.extend(o.name for o in elements(oNode.declarators))
            elif sKind == "ForVariableDeclaration":
                lReturn.append(oNode.declarator.name)
            elif sKind == "LoopGenerate" and text(oNode.genvar):
                lReturn.append(oNode.identifier)
            elif sKind in BLOCKS:
                for sAttribute in ("label", "beginName"):
                    oLabel = getattr(oNode, sAttribute, None)
                    if oLabel is not None and getattr(oLabel, "name", None) is not None and text(oLabel.name):
                        lReturn.append(oLabel.name)
    return sorted(lReturn, key=lambda o: o.location.offset)
