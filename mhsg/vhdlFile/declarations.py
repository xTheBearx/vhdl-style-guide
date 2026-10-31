# -*- coding: utf-8 -*-
"""
A list of the declarations in a VHDL file and the scopes they are visible in.

The list is built from the classified tokens, so it is available to every rule through vhdlFile.get_declarations().
"""

from mhsg.token import (
    alias_declaration,
    architecture_body,
    attribute_declaration,
    block_statement,
    case_generate_statement,
    component_declaration,
    component_instantiation_statement,
    constant_declaration,
    entity_declaration,
    enumeration_type_definition,
    file_declaration,
    for_generate_statement,
    full_type_declaration,
    function_specification,
    generic_clause,
    identifier_list,
    if_generate_statement,
    incomplete_type_declaration,
    interface_constant_declaration,
    interface_file_declaration,
    interface_incomplete_type_declaration,
    interface_signal_declaration,
    interface_unknown_declaration,
    interface_variable_declaration,
    iteration_scheme,
    loop_statement,
    package_body,
    package_declaration,
    parameter_specification,
    port_clause,
    procedure_specification,
    process_statement,
    protected_type_body,
    protected_type_declaration,
    record_type_definition,
    signal_declaration,
    subprogram_body,
    subprogram_declaration,
    subprogram_instantiation_declaration,
    subtype_declaration,
    variable_declaration,
)

# Tokens which open a scope, the kind of the scope and the tokens which close it
lScopeOpeners = [
    (entity_declaration.entity_keyword, "entity", (entity_declaration.semicolon,)),
    (architecture_body.architecture_keyword, "architecture", (architecture_body.semicolon,)),
    (package_declaration.package_keyword, "package", (package_declaration.semicolon,)),
    (package_body.package_keyword, "package_body", (package_body.semicolon,)),
    (process_statement.process_keyword, "process", (process_statement.semicolon,)),
    (block_statement.block_keyword, "block", (block_statement.semicolon,)),
    (for_generate_statement.for_keyword, "generate", (for_generate_statement.semicolon,)),
    (if_generate_statement.if_keyword, "generate", (if_generate_statement.semicolon,)),
    (case_generate_statement.case_keyword, "generate", (case_generate_statement.semicolon,)),
    (function_specification.function_keyword, "subprogram", (subprogram_body.semicolon, subprogram_declaration.semicolon)),
    (procedure_specification.procedure_keyword, "subprogram", (subprogram_body.semicolon, subprogram_declaration.semicolon)),
    (component_declaration.component_keyword, "component", (component_declaration.semicolon,)),
    (protected_type_declaration.protected_keyword, "protected", (protected_type_declaration.end_protected_keyword,)),
    (protected_type_body.protected_keyword, "protected_body", (protected_type_body.end_body_keyword,)),
    (record_type_definition.record_keyword, "record", (record_type_definition.end_record_keyword,)),
]

# Declarations and their kind
lDeclarationTokens = [
    (signal_declaration.identifier, "signal"),
    (constant_declaration.identifier, "constant"),
    (variable_declaration.identifier, "variable"),
    (file_declaration.identifier, "file"),
    (full_type_declaration.identifier, "type"),
    (incomplete_type_declaration.identifier, "type"),
    (subtype_declaration.identifier, "subtype"),
    (alias_declaration.alias_designator, "alias"),
    (attribute_declaration.identifier, "attribute"),
    (enumeration_type_definition.enumeration_literal, "enumeration_literal"),
    (parameter_specification.identifier, "loop_parameter"),
    (interface_incomplete_type_declaration.identifier, "type"),
    (subprogram_instantiation_declaration.identifier, "subprogram"),
    (process_statement.process_label, "label"),
    (block_statement.block_label, "label"),
    (for_generate_statement.generate_label, "label"),
    (if_generate_statement.generate_label, "label"),
    (case_generate_statement.generate_label, "label"),
    (loop_statement.loop_label, "label"),
    (component_instantiation_statement.instantiation_label, "label"),
]

# Interface declarations, whose kind depends on the list they are in
lInterfaceTokens = (
    interface_constant_declaration.identifier,
    interface_signal_declaration.identifier,
    interface_variable_declaration.identifier,
    interface_file_declaration.identifier,
    interface_unknown_declaration.identifier,
)

# Names of design units and subprograms, which are declared in the scope around the one they open
lScopeNameTokens = (
    entity_declaration.identifier,
    architecture_body.identifier,
    package_declaration.identifier,
    package_body.package_simple_name,
    component_declaration.identifier,
    function_specification.designator,
    procedure_specification.designator,
)

dScopeNameKinds = {
    entity_declaration.identifier: "entity",
    architecture_body.identifier: "architecture",
    package_declaration.identifier: "package",
    component_declaration.identifier: "component",
    function_specification.designator: "function",
    procedure_specification.designator: "procedure",
}


class Declaration:
    def __init__(self, sName, sKind, oScope, iIndex):
        self.name = sName
        self.lower_name = sName.lower()
        self.kind = sKind
        self.scope = oScope
        self.index = iIndex

    def __repr__(self):
        return f"Declaration({self.name}, {self.kind}, {self.scope.kind} {self.scope.name})"


class Scope:
    def __init__(self, sKind, iStart, oParent):
        self.kind = sKind
        self.name = None
        self.start = iStart
        self.end = None
        self.parent = oParent
        self.children = []
        self.declarations = []
        # The name of the entity an architecture belongs to
        self.entity_name = None

    def contains(self, iIndex):
        return self.start <= iIndex <= self.end

    def find_local(self, sLowerName):
        return [oDeclaration for oDeclaration in self.declarations if oDeclaration.lower_name == sLowerName]

    def __repr__(self):
        return f"Scope({self.kind}, {self.name}, {self.start}-{self.end})"


class DeclarationList:
    def __init__(self, lTokens):
        self.root = Scope("design_file", 0, None)
        self.root.end = len(lTokens)
        self.scopes = [self.root]
        self.declarations = []
        build(self, lTokens)

    def get_scope_at(self, iIndex):
        """
        Returns the innermost scope containing the token index.
        """
        oScope = self.root
        while True:
            for oChild in oScope.children:
                if oChild.contains(iIndex):
                    oScope = oChild
                    break
            else:
                return oScope

    def find(self, sName, iIndex):
        """
        Returns the declarations of a name visible at the token index, innermost first.
        A name declared in an inner scope hides the same name in outer scopes.
        """
        sLowerName = sName.lower()
        for oScope in self.get_visible_scopes(iIndex):
            lFound = oScope.find_local(sLowerName)
            if len(lFound) > 0:
                return lFound
        return []

    def find_all(self, sName):
        """
        Returns every declaration of a name in the file.
        """
        sLowerName = sName.lower()
        return [oDeclaration for oDeclaration in self.declarations if oDeclaration.lower_name == sLowerName]

    def get_visible_scopes(self, iIndex):
        """
        Returns the scopes whose declarations are visible at the token index, innermost first.
        An architecture also sees its entity, a package body its package, and every unit the packages in the file.
        """
        lReturn = []
        oScope = self.get_scope_at(iIndex)
        while oScope is not None:
            if oScope.kind != "record":
                lReturn.append(oScope)
            if oScope.kind == "architecture":
                lReturn.extend(self.get_units("entity", oScope.entity_name))
            elif oScope.kind == "package_body":
                lReturn.extend(self.get_units("package", oScope.name))
            oScope = oScope.parent
        for oPackage in self.get_units("package", None):
            if oPackage not in lReturn:
                lReturn.append(oPackage)
        return lReturn

    def get_units(self, sKind, sName):
        return [oScope for oScope in self.root.children if oScope.kind == sKind and (sName is None or (oScope.name or "").lower() == sName.lower())]


def build(self, lTokens):
    lStack = [self.root]
    sInterfaceKind = "parameter"
    for iIndex, oToken in enumerate(lTokens):
        oScope = lStack[-1]

        # Loop scopes start at the iteration scheme, or at the loop keyword of a loop without one
        if isinstance(oToken, (iteration_scheme.for_keyword, iteration_scheme.while_keyword)):
            lStack.append(open_scope(self, "loop", iIndex, oScope))
            lStack[-1].bWaitingForLoopKeyword = True
            continue
        if isinstance(oToken, loop_statement.loop_keyword):
            if oScope.kind == "loop" and getattr(oScope, "bWaitingForLoopKeyword", False):
                oScope.bWaitingForLoopKeyword = False
            else:
                lStack.append(open_scope(self, "loop", iIndex, oScope))
            continue
        if isinstance(oToken, loop_statement.semicolon):
            close_scope(lStack, "loop", iIndex)
            continue

        bOpened = False
        for oOpener, sKind, tClosers in lScopeOpeners:
            if isinstance(oToken, oOpener):
                lStack.append(open_scope(self, sKind, iIndex, oScope))
                bOpened = True
                break
        if bOpened:
            continue

        for oOpener, sKind, tClosers in lScopeOpeners:
            if isinstance(oToken, tClosers):
                close_scope(lStack, sKind, iIndex)
                break

        if isinstance(oToken, generic_clause.generic_keyword):
            sInterfaceKind = "generic"
        elif isinstance(oToken, port_clause.port_keyword):
            sInterfaceKind = "port"
        elif isinstance(oToken, (generic_clause.semicolon, port_clause.semicolon)):
            sInterfaceKind = "parameter"

        if isinstance(oToken, lScopeNameTokens):
            oScope.name = oToken.get_value()
            if oToken.__class__ in dScopeNameKinds and oScope.parent is not None:
                add_declaration(self, oToken.get_value(), dScopeNameKinds[oToken.__class__], oScope.parent, iIndex)
        elif isinstance(oToken, architecture_body.entity_name):
            oScope.entity_name = oToken.get_value()
        elif isinstance(oToken, lInterfaceTokens):
            add_declaration(self, oToken.get_value(), sInterfaceKind, oScope, iIndex)
        elif isinstance(oToken, identifier_list.identifier) and oScope.kind == "record":
            add_declaration(self, oToken.get_value(), "record_element", oScope, iIndex)
        else:
            for oClass, sKind in lDeclarationTokens:
                if isinstance(oToken, oClass):
                    add_declaration(self, oToken.get_value(), sKind, oScope, iIndex)
                    break
    for oScope in lStack[1:]:
        oScope.end = len(lTokens)


def open_scope(self, sKind, iIndex, oParent):
    oScope = Scope(sKind, iIndex, oParent)
    oParent.children.append(oScope)
    self.scopes.append(oScope)
    return oScope


def close_scope(lStack, sKind, iIndex):
    # Close the innermost open scope of the kind, and any scopes left open inside it by malformed code
    for iScope in range(len(lStack) - 1, 0, -1):
        if lStack[iScope].kind == sKind:
            for oScope in lStack[iScope:]:
                oScope.end = iIndex
            del lStack[iScope:]
            return


def add_declaration(self, sName, sKind, oScope, iIndex):
    oDeclaration = Declaration(sName, sKind, oScope, iIndex)
    oScope.declarations.append(oDeclaration)
    self.declarations.append(oDeclaration)
