# -*- coding: utf-8 -*-
"""
A model of the statement part of each architecture in a file, built from the classified tokens.

It records processes with their sensitivity lists and statement trees, concurrent signal
assignments and component instantiations. The lint rules work on this model instead of on
the tokens. It describes what the code says, not what it means: names are not resolved to
declarations here, so rules look them up in vhdlFile.get_declarations() where needed.
"""

import re

from mhsg import parser
from mhsg.token import mode as token_mode

reName = re.compile(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$", re.IGNORECASE)

# Reserved words that can appear inside an index or slice
INDEX_KEYWORDS = {"to", "downto", "others", "and", "or", "not", "xor", "nand", "nor", "xnor", "mod", "rem", "abs", "sll", "srl", "sla", "sra", "rol", "ror", "open"}

TRIVIA = (parser.whitespace, parser.carriage_return, parser.blank_line, parser.comment)

SIGNAL_TARGET_MODULES = {
    "simple_waveform_assignment",
    "conditional_waveform_assignment",
    "selected_waveform_assignment",
    "simple_force_assignment",
    "simple_release_assignment",
    "conditional_force_assignment",
    "selected_force_assignment",
}
VARIABLE_TARGET_MODULES = {"simple_variable_assignment", "conditional_variable_assignment", "selected_variable_assignment"}
CONCURRENT_MODULES = {
    "concurrent_simple_signal_assignment",
    "concurrent_conditional_signal_assignment",
    "concurrent_selected_signal_assignment",
    "concurrent_signal_assignment_statement",
}

IF_STOP = {("if_statement", "elsif_keyword"), ("if_statement", "else_keyword"), ("if_statement", "end_keyword")}
CASE_STOP = {("case_statement_alternative", "when_keyword"), ("case_statement", "end_keyword")}
LOOP_STOP = {("loop_statement", "end_keyword")}
PROCESS_STOP = {("process_statement", "end_keyword")}

LOOP_START = {("loop_statement", "loop_label"), ("iteration_scheme", "for_keyword"), ("iteration_scheme", "while_keyword"), ("loop_statement", "loop_keyword")}

METAVALUES = set("uxzw-")


def kind(oToken):
    """Returns the module and class name of a token, for example ("if_statement", "if_keyword")."""
    return oToken.__class__.__module__.rsplit(".", 1)[-1], oToken.__class__.__name__


def is_trivia(oToken):
    return isinstance(oToken, TRIVIA) or kind(oToken)[0] == "pragma"


# Attributes whose value does not depend on the value of their prefix, such as a'length
STATIC_ATTRIBUTES = {
    "length", "range", "reverse_range", "left", "right", "high", "low", "ascending", "element", "subtype", "base",
    "image", "value", "pos", "val", "succ", "pred", "leftof", "rightof", "simple_name", "instance_name", "path_name",
}

NAME_KINDS = (("parser", "todo"), ("todo", "name"), ("association_element", "actual_part"))


def name_of(oToken):
    """Returns the lower case name of a token that names something in an expression, or None."""
    if kind(oToken) not in NAME_KINDS:
        return None
    sValue = oToken.get_value()
    if sValue is None or not reName.match(sValue):
        return None
    return sValue.lower()


def base_name(sName):
    return sName.split(".")[0].split("(")[0]


class Statement:
    """A statement in a statement sequence."""

    def __init__(self, sKind, iIndex, iLine):
        self.kind = sKind
        self.index = iIndex
        self.line = iLine


class Assignment(Statement):
    """
    A signal or variable assignment.
    target is the whole target in lower case without spaces, for example "out2(3)";
    base is the name being assigned, for example "out2"; indexed is True for a slice, element or record field.
    """

    def __init__(self, sKind, iIndex, iLine, lTargetTokens, lReads):
        super().__init__(sKind, iIndex, iLine)
        lTargetTokens = [o for o in lTargetTokens if not is_trivia(o)]
        lValues = [o.get_value() for o in lTargetTokens]
        self.target = "".join(lValues).lower()
        self.base = base_name(lValues[0].lower()) if lValues else ""
        self.indexed = len(lValues) > 1 or "." in (lValues[0] if lValues else "")
        # The tokens of an index are classified as part of the target, so names are found by their value
        lIndexNames = [(o.get_value() or "").lower() for o in lTargetTokens[1:] if reName.match(o.get_value() or "")]
        lIndexNames = [s for s in lIndexNames if s not in INDEX_KEYWORDS]
        # An index made only of literals selects a fixed part; a name in the index, such as mem(addr), does not
        self.static_index = not any(lIndexNames)
        # Names read for the value assigned, and in addition the names in the index of the target
        self.value_reads = lReads
        self.reads = lReads + [s for s in lIndexNames if s]
        # The record path of the target without any index, such as "status.phy_ready" for status.phy_ready(0)
        self.path = lValues[0].lower().split("(")[0] if lValues else ""

    def covers(self):
        """
        Returns the part of the signal this assignment sets for certain: the target itself, such as out2(3) or r.f,
        or the whole signal for an index that is a name, such as mem(addr), which may set any element.
        """
        return self.target if self.static_index else self.base


class If(Statement):
    """
    An if statement; branches is a list of (condition tokens, statements, line, token index), with None as the
    condition of an else branch. has_else tells if the last branch is an else.
    """

    def __init__(self, iIndex, iLine):
        super().__init__("if", iIndex, iLine)
        self.branches = []
        self.has_else = False


class Case(Statement):
    """A case statement; alternatives is a list of Alternative."""

    def __init__(self, iIndex, iLine):
        super().__init__("case", iIndex, iLine)
        # True for a matching case statement, case?, where - matches any value
        self.matching = False
        self.selector = []
        self.alternatives = []


class Alternative:
    def __init__(self, iIndex, iLine):
        self.index = iIndex
        self.line = iLine
        # Choices in lower case for comparison, and as written for messages
        self.choices = []
        self.choice_texts = []
        self.choice_indexes = []
        self.others = False
        self.statements = []


class Loop(Statement):
    def __init__(self, iIndex, iLine):
        super().__init__("loop", iIndex, iLine)
        self.header = []
        self.parameter = None
        self.statements = []


class Other(Statement):
    """Any other statement: wait, null, procedure call, report, assert, exit, next, return."""

    def __init__(self, sKind, iIndex, iLine, lReads):
        super().__init__(sKind, iIndex, iLine)
        self.reads = lReads


class Process:
    def __init__(self, iIndex, iLine):
        self.index = iIndex
        self.line = iLine
        self.label = None
        # None when there is no sensitivity list, "all" for process (all), else the lower case names
        self.sensitivity = None
        self.sensitivity_lines = {}
        self.variables = set()
        self.statements = []
        self.has_wait = False
        self.clock = None
        self.generate = ()


class ConcurrentAssignment(Assignment):
    """
    A concurrent signal assignment. clocked is True for a register such as q <= d when rising_edge(clk).
    generate holds the generate branches it is in, see Model.lGenerate.
    """

    def __init__(self, iIndex, iLine, lTargetTokens, lReads):
        super().__init__("signal", iIndex, iLine, lTargetTokens, lReads)
        self.clocked = False
        self.generate = ()


class Instance:
    """
    A component or entity instantiation.
    associations is a list of (formal, actual, line); formal is None for positional associations
    and actual is "open" for an open port.
    """

    def __init__(self, iIndex, iLine):
        self.index = iIndex
        self.line = iLine
        self.label = None
        self.unit = None
        self.unit_kind = "component"
        self.associations = []
        self.has_port_map = False
        self.generate = ()


class Architecture:
    def __init__(self, iIndex, iLine):
        self.index = iIndex
        self.line = iLine
        self.name = None
        self.entity = None
        self.end = None
        self.processes = []
        self.assignments = []
        self.instances = []


class Model:
    """The architectures of a file and the ports of the entities declared in it."""

    def __init__(self, oFile):
        self.oFile = oFile
        self.lTokens = oFile.lAllObjects
        self.oTokenMap = oFile.get_token_map()
        self.architectures = []
        # The condition of each if generate statement by the token index of its if keyword
        self.dGenerateConditions = {}
        # Lower case entity name to a list of (port name, mode, line)
        self.entity_ports = {}
        # Lower case component name to a list of (port name, mode, line)
        self.component_ports = {}
        self._build()

    def line(self, iIndex):
        return self.oTokenMap.get_line_number_of_index(iIndex)

    def _build(self):
        iIndex = 0
        iLength = len(self.lTokens)
        while iIndex < iLength:
            sModule, sName = kind(self.lTokens[iIndex])
            if (sModule, sName) == ("architecture_body", "architecture_keyword"):
                iIndex = self._architecture(iIndex)
            elif (sModule, sName) in (("entity_declaration", "entity_keyword"), ("component_declaration", "component_keyword")):
                iIndex = self._ports(iIndex, sModule)
            else:
                iIndex += 1

    def _ports(self, iIndex, sModule):
        """Records the ports of an entity or component declaration, and returns the index after it."""
        sName = None
        lPorts = []
        bPortClause = False
        sMode = "in"
        lNames = []
        iIndex += 1
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            sTokenModule, sTokenName = kind(oToken)
            if sTokenModule == sModule and sTokenName == "identifier" and sName is None:
                sName = oToken.get_value().lower()
            elif sTokenModule == sModule and sTokenName == "semicolon":
                break
            elif sTokenModule == "port_clause" and sTokenName == "port_keyword":
                bPortClause = True
            elif bPortClause and sTokenModule in ("interface_signal_declaration", "interface_unknown_declaration") and sTokenName == "identifier":
                lNames.append((oToken.get_value().lower(), self.line(iIndex)))
            elif bPortClause and isinstance(oToken, token_mode.mode):
                sMode = oToken.get_value().lower()
            elif bPortClause and (sTokenModule, sTokenName) in (("interface_list", "semicolon"), ("port_clause", "close_parenthesis")):
                lPorts.extend((sPort, sMode, iLine) for sPort, iLine in lNames)
                lNames = []
                sMode = "in"
                if sTokenModule == "port_clause":
                    bPortClause = False
            iIndex += 1
        if sName is not None:
            dTarget = self.entity_ports if sModule == "entity_declaration" else self.component_ports
            dTarget[sName] = lPorts
        return iIndex + 1

    def _architecture(self, iIndex):
        oArchitecture = Architecture(iIndex, self.line(iIndex))
        iIndex += 1
        bStatementPart = False
        # The generate statements around the current statement, as (token index of the generate, branch number)
        self.lGenerate = []
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("architecture_body", "identifier"):
                oArchitecture.name = oToken.get_value().lower()
            elif tKind == ("architecture_body", "entity_name"):
                oArchitecture.entity = oToken.get_value().lower()
            elif tKind == ("architecture_body", "begin_keyword"):
                bStatementPart = True
            elif not bStatementPart and tKind == ("component_declaration", "component_keyword"):
                iIndex = self._ports(iIndex, "component_declaration")
                continue
            elif tKind == ("architecture_body", "semicolon"):
                oArchitecture.end = iIndex
                self.architectures.append(oArchitecture)
                return iIndex + 1
            elif bStatementPart and self._generate(tKind, iIndex):
                pass
            elif bStatementPart:
                iNext = self._concurrent_statement(iIndex, oArchitecture)
                if iNext is not None:
                    iIndex = iNext
                    continue
            iIndex += 1
        oArchitecture.end = iIndex
        self.architectures.append(oArchitecture)
        return iIndex

    def _generate_condition(self, iIndex):
        """Returns the condition of the first branch of an if generate statement, normalized for comparison."""
        lValues = []
        iIndex += 1
        while iIndex < len(self.lTokens) and kind(self.lTokens[iIndex]) != ("if_generate_statement", "generate_keyword"):
            oToken = self.lTokens[iIndex]
            if not is_trivia(oToken) and not isinstance(oToken, (parser.open_parenthesis, parser.close_parenthesis)):
                lValues.append((oToken.get_value() or "").lower())
            iIndex += 1
        return " ".join(lValues)

    def _generate(self, tKind, iIndex):
        """
        Tracks the branches of if and case generate statements, so statements in different branches of the same
        generate statement can be told apart. Returns True if the token was a generate keyword.
        """
        if tKind == ("if_generate_statement", "if_keyword"):
            self.lGenerate.append((iIndex, 0))
            self.dGenerateConditions[iIndex] = self._generate_condition(iIndex)
        elif tKind == ("for_generate_statement", "for_keyword"):
            self.lGenerate.append((iIndex, 0))
        elif tKind == ("case_generate_statement", "case_keyword"):
            self.lGenerate.append((iIndex, -1))
            self.dGenerateConditions[iIndex] = "case"
        elif tKind in (("if_generate_statement", "elsif_keyword"), ("if_generate_statement", "else_keyword"), ("case_generate_alternative", "when_keyword")):
            if self.lGenerate:
                iGenerate, iBranch = self.lGenerate.pop()
                self.lGenerate.append((iGenerate, iBranch + 1))
        elif tKind in (("if_generate_statement", "end_keyword"), ("case_generate_statement", "end_keyword"), ("for_generate_statement", "end_keyword")):
            if self.lGenerate:
                self.lGenerate.pop()
        else:
            return False
        return True

    def _concurrent_statement(self, iIndex, oArchitecture):
        """Parses the concurrent statement starting at iIndex and returns the index after it, or None if none starts there."""
        sModule, sName = kind(self.lTokens[iIndex])
        if sModule == "process_statement" and sName in ("process_label", "process_keyword", "postponed_keyword"):
            return self._process(iIndex, oArchitecture)
        if sModule == "component_instantiation_statement" and sName == "instantiation_label":
            return self._instance(iIndex, oArchitecture)
        if sModule in CONCURRENT_MODULES:
            return self._concurrent_assignment(iIndex, oArchitecture)
        return None

    def _until_semicolon(self, iIndex):
        """Returns the index of the next semicolon token at or after iIndex."""
        while iIndex < len(self.lTokens) and not isinstance(self.lTokens[iIndex], parser.semicolon):
            iIndex += 1
        return iIndex

    def _concurrent_assignment(self, iIndex, oArchitecture):
        iEnd = self._until_semicolon(iIndex)
        lTokens = self.lTokens[iIndex:iEnd]
        lTarget = [o for o in lTokens if kind(o)[0] in CONCURRENT_MODULES and kind(o)[1] == "target"]
        lReads = names([o for o in lTokens if kind(o)[1] != "target"])
        oAssignment = ConcurrentAssignment(iIndex, self.line(iIndex), lTarget, lReads)
        oAssignment.clocked = bool(edges(lTokens))
        oAssignment.generate = tuple(self.lGenerate)
        oArchitecture.assignments.append(oAssignment)
        return iEnd + 1

    def _instance(self, iIndex, oArchitecture):
        oInstance = Instance(iIndex, self.line(iIndex))
        oInstance.label = self.lTokens[iIndex].get_value().lower()
        iDepth = 0
        lFormal = []
        lActual = []
        iAssociationLine = None
        bPortMap = False
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("component_instantiation_statement", "semicolon"):
                break
            if tKind in (("instantiated_unit", "entity_name"), ("instantiated_unit", "component_name")):
                oInstance.unit = oToken.get_value().lower()
                oInstance.unit_kind = "entity" if tKind[1] == "entity_name" else "component"
            elif tKind == ("port_map_aspect", "open_parenthesis"):
                bPortMap = True
                oInstance.has_port_map = True
            elif bPortMap and tKind == ("port_map_aspect", "close_parenthesis"):
                self._add_association(oInstance, lFormal, lActual, iAssociationLine)
                bPortMap = False
            elif bPortMap:
                if isinstance(oToken, parser.open_parenthesis):
                    iDepth += 1
                elif isinstance(oToken, parser.close_parenthesis):
                    iDepth -= 1
                if tKind == ("association_list", "comma") and iDepth == 0:
                    self._add_association(oInstance, lFormal, lActual, iAssociationLine)
                    lFormal, lActual, iAssociationLine = [], [], None
                elif tKind == ("association_element", "formal_part"):
                    lFormal.append(oToken)
                    iAssociationLine = iAssociationLine or self.line(iIndex)
                elif not is_trivia(oToken) and tKind != ("association_element", "assignment"):
                    lActual.append(oToken)
                    iAssociationLine = iAssociationLine or self.line(iIndex)
            iIndex += 1
        oInstance.generate = tuple(self.lGenerate)
        oArchitecture.instances.append(oInstance)
        return iIndex + 1

    def _add_association(self, oInstance, lFormal, lActual, iLine):
        if not lFormal and not lActual:
            return
        sFormal = base_name(lFormal[0].get_value().lower()) if lFormal else None
        sActual = "".join(o.get_value() for o in lActual).lower()
        oInstance.associations.append((sFormal, sActual, iLine))

    def _process(self, iIndex, oArchitecture):
        oProcess = Process(iIndex, self.line(iIndex))
        bSensitivity = False
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("process_statement", "process_label"):
                oProcess.label = oToken.get_value().lower()
            elif tKind == ("process_statement", "open_parenthesis"):
                bSensitivity = True
                oProcess.sensitivity = []
            elif tKind == ("process_statement", "close_parenthesis"):
                bSensitivity = False
            elif bSensitivity and tKind == ("process_sensitivity_list", "all_keyword"):
                oProcess.sensitivity = "all"
            elif bSensitivity and isinstance(oProcess.sensitivity, list):
                sName = name_of(oToken)
                if sName is not None:
                    oProcess.sensitivity.append(sName)
                    oProcess.sensitivity_lines[sName] = self.line(iIndex)
            elif tKind == ("variable_declaration", "identifier"):
                oProcess.variables.add(oToken.get_value().lower())
            elif tKind == ("process_statement", "begin_keyword"):
                oProcess.statements, iIndex = self._sequence(iIndex + 1, PROCESS_STOP)
                iIndex = self._until_semicolon(iIndex)
                break
            iIndex += 1
        oProcess.generate = tuple(self.lGenerate)
        oProcess.has_wait = any(o.kind == "wait" for o in walk(oProcess.statements))
        oProcess.clock = find_clock(oProcess)
        oArchitecture.processes.append(oProcess)
        return iIndex + 1

    def _skip_trivia(self, iIndex):
        while iIndex < len(self.lTokens) and is_trivia(self.lTokens[iIndex]):
            iIndex += 1
        return iIndex

    def _sequence(self, iIndex, setStop):
        """Parses statements until a token in setStop, and returns (statements, index of that token)."""
        lStatements = []
        while True:
            iIndex = self._skip_trivia(iIndex)
            if iIndex >= len(self.lTokens):
                return lStatements, iIndex
            tKind = kind(self.lTokens[iIndex])
            if tKind in setStop:
                return lStatements, iIndex
            if tKind[0] == "if_statement" and tKind[1] in ("if_label", "if_keyword"):
                oStatement, iIndex = self._if(iIndex)
            elif tKind[0] == "case_statement" and tKind[1] in ("case_label", "case_keyword"):
                oStatement, iIndex = self._case(iIndex)
            elif tKind in LOOP_START:
                oStatement, iIndex = self._loop(iIndex)
            else:
                oStatement, iIndex = self._simple(iIndex)
            lStatements.append(oStatement)

    def _if(self, iIndex):
        oIf = If(iIndex, self.line(iIndex))
        lCondition = None
        while iIndex < len(self.lTokens):
            tKind = kind(self.lTokens[iIndex])
            if tKind in (("if_statement", "if_keyword"), ("if_statement", "elsif_keyword")):
                lCondition = []
                iBranch = iIndex
            elif tKind == ("if_statement", "else_keyword"):
                iBranch = iIndex
                lStatements, iIndex = self._sequence(iIndex + 1, IF_STOP)
                oIf.branches.append((None, lStatements, self.line(iBranch), iBranch))
                oIf.has_else = True
                continue
            elif tKind == ("if_statement", "then_keyword"):
                lStatements, iIndex = self._sequence(iIndex + 1, IF_STOP)
                oIf.branches.append((lCondition, lStatements, self.line(iBranch), iBranch))
                lCondition = None
                continue
            elif tKind == ("if_statement", "end_keyword"):
                return oIf, self._until_semicolon(iIndex) + 1
            elif lCondition is not None and not is_trivia(self.lTokens[iIndex]):
                lCondition.append(self.lTokens[iIndex])
            iIndex += 1
        return oIf, iIndex

    def _case(self, iIndex):
        oCase = Case(iIndex, self.line(iIndex))
        bSelector = False
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("case_statement", "case_keyword"):
                bSelector = True
            elif tKind == ("case_statement", "question_mark"):
                oCase.matching = True
            elif tKind == ("case_statement", "is_keyword") and bSelector:
                bSelector = False
            elif tKind == ("case_statement_alternative", "when_keyword"):
                oAlternative = Alternative(iIndex, self.line(iIndex))
                iIndex = self._choices(iIndex + 1, oAlternative)
                oAlternative.statements, iIndex = self._sequence(iIndex + 1, CASE_STOP)
                oCase.alternatives.append(oAlternative)
                continue
            elif tKind == ("case_statement", "end_keyword"):
                return oCase, self._until_semicolon(iIndex) + 1
            elif bSelector and not is_trivia(oToken):
                oCase.selector.append(oToken)
            iIndex += 1
        return oCase, iIndex

    def _choices(self, iIndex, oAlternative):
        """Records the choices of a case alternative and returns the index of its =>."""
        lChoice = []
        iDepth = 0
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("case_statement_alternative", "assignment"):
                break
            if isinstance(oToken, parser.open_parenthesis):
                iDepth += 1
            elif isinstance(oToken, parser.close_parenthesis):
                iDepth -= 1
            if tKind[0] == "choice" and tKind[1] == "others_keyword":
                oAlternative.others = True
            elif tKind[1] == "bar" and iDepth == 0:
                self._add_choice(oAlternative, lChoice)
                lChoice = []
            elif not is_trivia(oToken):
                lChoice.append((oToken, iIndex))
            iIndex += 1
        self._add_choice(oAlternative, lChoice)
        return iIndex

    def _add_choice(self, oAlternative, lChoice):
        if lChoice:
            oAlternative.choices.append("".join(o.get_value() for o, i in lChoice).lower())
            oAlternative.choice_texts.append("".join(o.get_value() for o, i in lChoice))
            oAlternative.choice_indexes.append(lChoice[0][1])

    def _loop(self, iIndex):
        oLoop = Loop(iIndex, self.line(iIndex))
        while iIndex < len(self.lTokens):
            oToken = self.lTokens[iIndex]
            tKind = kind(oToken)
            if tKind == ("parameter_specification", "identifier"):
                oLoop.parameter = oToken.get_value().lower()
            elif tKind == ("loop_statement", "loop_keyword"):
                oLoop.statements, iIndex = self._sequence(iIndex + 1, LOOP_STOP)
                return oLoop, self._until_semicolon(iIndex) + 1
            elif not is_trivia(oToken):
                oLoop.header.append(oToken)
            iIndex += 1
        return oLoop, iIndex

    def _simple(self, iIndex):
        iStart = iIndex
        iEnd = self._until_semicolon(iIndex)
        lTokens = self.lTokens[iStart:iEnd]
        iLine = self.line(iStart)
        lSignalTarget = [o for o in lTokens if kind(o)[0] in SIGNAL_TARGET_MODULES and kind(o)[1] == "target"]
        lVariableTarget = [o for o in lTokens if kind(o)[0] in VARIABLE_TARGET_MODULES and kind(o)[1] in ("target", "simple_name")]
        lReads = names([o for o in lTokens if o not in lSignalTarget and o not in lVariableTarget])
        if lSignalTarget:
            oStatement = Assignment("signal", iStart, iLine, lSignalTarget, lReads)
        elif lVariableTarget:
            oStatement = Assignment("variable", iStart, iLine, lVariableTarget, lReads)
        else:
            sModule = kind(self.lTokens[iStart])[0]
            sKind = {"wait_statement": "wait", "null_statement": "null"}.get(sModule, "other")
            oStatement = Other(sKind, iStart, iLine, lReads)
        return oStatement, iEnd + 1


def walk(lStatements):
    """Yields every statement in a statement tree, depth first."""
    for oStatement in lStatements:
        yield oStatement
        if isinstance(oStatement, If):
            for tBranch in oStatement.branches:
                yield from walk(tBranch[1])
        elif isinstance(oStatement, Case):
            for oAlternative in oStatement.alternatives:
                yield from walk(oAlternative.statements)
        elif isinstance(oStatement, Loop):
            yield from walk(oStatement.statements)


def assignments(lStatements, sKind="signal"):
    """Returns the assignments of a kind anywhere in a statement tree."""
    return [o for o in walk(lStatements) if isinstance(o, Assignment) and o.kind == sKind]


def reads(lStatements):
    """Returns the lower case names read anywhere in a statement tree, including conditions, selectors and loop ranges."""
    lReturn = []
    for oStatement in walk(lStatements):
        if isinstance(oStatement, (Assignment, Other)):
            lReturn.extend(oStatement.reads)
        elif isinstance(oStatement, If):
            for tBranch in oStatement.branches:
                lReturn.extend(names(tBranch[0] or []))
        elif isinstance(oStatement, Case):
            lReturn.extend(names(oStatement.selector))
        elif isinstance(oStatement, Loop):
            lReturn.extend(names(oStatement.header))
    return lReturn


def names(lTokens):
    """
    Returns the lower case names whose values are read in a list of tokens.
    The prefix of an attribute such as a'length or a'range is left out, since its value is not read.
    """
    lReturn = []
    lSignificant = [o for o in lTokens if not is_trivia(o)]
    for iIndex, oToken in enumerate(lSignificant):
        sName = name_of(oToken)
        if sName is None:
            continue
        if iIndex + 2 < len(lSignificant) and isinstance(lSignificant[iIndex + 1], parser.tic):
            if (lSignificant[iIndex + 2].get_value() or "").lower() in STATIC_ATTRIBUTES:
                continue
        lReturn.append(sName)
    return lReturn


def edges(lTokens):
    """Returns (clock name, edge) for each clock edge in a condition: rising_edge(clk), falling_edge(clk) or clk'event."""
    lReturn = []
    lSignificant = [o for o in lTokens if not is_trivia(o)]
    for iIndex, oToken in enumerate(lSignificant):
        sValue = (oToken.get_value() or "").lower()
        if sValue in ("rising_edge", "falling_edge"):
            for oNext in lSignificant[iIndex + 1 :]:
                sName = name_of(oNext)
                if sName is not None:
                    lReturn.append((base_name(sName), sValue.split("_")[0]))
                    break
        elif isinstance(oToken, parser.tic) and iIndex > 0 and iIndex + 1 < len(lSignificant):
            if (lSignificant[iIndex + 1].get_value() or "").lower() == "event":
                sName = name_of(lSignificant[iIndex - 1])
                if sName is not None:
                    lReturn.append((base_name(sName), "event"))
    return lReturn


def reset_condition(lTokens):
    """
    Returns (name, active level) for the signal a reset condition tests, such as rst = '1', rst_n = '0', not rst,
    rst, or rst = RST_POLARITY_G and RST_ASYNC_G. The level is "1", "0", or None when it is compared with a name.
    In a condition of several terms, a term with a reset name is preferred. Returns None if no term tests one signal.
    """
    from mhsg.rules.port.rule_028 import is_reset_name

    lTerms = [[]]
    for oToken in lTokens:
        if is_trivia(oToken) or isinstance(oToken, (parser.open_parenthesis, parser.close_parenthesis)):
            continue
        if (oToken.get_value() or "").lower() in ("and", "or"):
            lTerms.append([])
        else:
            lTerms[-1].append(oToken)
    lCandidates = [t for t in (term_condition(l) for l in lTerms) if t is not None]
    if len(lCandidates) == 1:
        return lCandidates[0][:2]
    # A comparison such as rst = RST_POLARITY_G is preferred over a bare name such as RST_ASYNC_G, which is
    # usually a generic; then a name that looks like a reset
    for bComparison in (True, False):
        for sName, sLevel, bIsComparison in lCandidates:
            if bIsComparison == bComparison and is_reset_name(sName):
                return sName, sLevel
    return None


def term_condition(lSignificant):
    """Returns (name, level, is a comparison) for one term of a condition that tests one name, or None."""
    lValues = [(o.get_value() or "").lower() for o in lSignificant]
    if len(lValues) == 1 and name_of(lSignificant[0]):
        return base_name(lValues[0]), "1", False
    if len(lValues) == 2 and lValues[0] == "not" and name_of(lSignificant[1]):
        return base_name(lValues[1]), "0", False
    if len(lValues) == 3 and name_of(lSignificant[0]) and lValues[1] in ("=", "/="):
        sLevel = {"'1'": "1", "'0'": "0", "true": "1", "false": "0"}.get(lValues[2])
        if sLevel is not None and lValues[1] == "/=":
            sLevel = "0" if sLevel == "1" else "1"
        return base_name(lValues[0]), sLevel, True
    return None


class Reset:
    """A reset of a clocked process: the signal, its active level "1" or "0", its style "async" or "sync", and where it is tested."""

    def __init__(self, sName, sLevel, sStyle, iLine, iIndex):
        self.name = sName
        self.level = sLevel
        self.style = sStyle
        self.line = iLine
        self.index = iIndex


class Clock:
    """
    How a clocked process is built.
    name and edge are the clock; clock_branch holds the statements run on the clock edge.
    reset is a Reset or None; reset_branch holds its statements.
    """

    def __init__(self, sName, sEdge):
        self.name = sName
        self.edge = sEdge
        self.clock_branch = []
        self.reset = None
        self.reset_branch = []
        # The conditions of the branches before the clock edge, the asynchronous controls of the process
        self.async_conditions = []


def find_clock(oProcess):
    """Returns a Clock for a process with a clock edge in an if statement at its top level, otherwise None."""
    for oStatement in oProcess.statements:
        if not isinstance(oStatement, If):
            continue
        for iBranch, (lCondition, lBranch, iLine, iIndex) in enumerate(oStatement.branches):
            lEdges = edges(lCondition or [])
            if not lEdges:
                continue
            oClock = Clock(*lEdges[0])
            oClock.clock_branch = lBranch
            if iBranch > 0:
                lResetCondition, lResetBranch, iResetLine, iResetIndex = oStatement.branches[0]
                oClock.async_conditions = [tBranch[0] or [] for tBranch in oStatement.branches[:iBranch]]
                oClock.reset_branch = lResetBranch
                tReset = reset_condition(lResetCondition or [])
                sName, sLevel = tReset if tReset is not None else (None, None)
                oClock.reset = Reset(sName, sLevel, "async", iResetLine, iResetIndex)
            else:
                find_sync_reset(oClock)
            return oClock
    return None


def find_sync_reset(oClock):
    """Records a synchronous reset: an if statement first in the clock branch that tests one signal whose name looks like a reset."""
    from mhsg.rules.port.rule_028 import is_reset_name

    lStatements = [o for o in oClock.clock_branch]
    if not lStatements or not isinstance(lStatements[0], If):
        return
    lCondition, lBranch, iLine, iIndex = lStatements[0].branches[0]
    tReset = reset_condition(lCondition or [])
    if tReset is not None and is_reset_name(tReset[0]):
        oClock.reset = Reset(tReset[0], tReset[1], "sync", iLine, iIndex)
        oClock.reset_branch = lBranch


def has_edge(oProcess):
    """Returns True if any if condition in the process tests a clock edge, wherever it is."""
    for oStatement in walk(oProcess.statements):
        if isinstance(oStatement, If) and any(edges(tBranch[0] or []) for tBranch in oStatement.branches):
            return True
    return False


def sequences(lStatements):
    """Yields each statement sequence of a tree: the list itself, and every branch, alternative and loop body in it."""
    yield lStatements
    for oStatement in lStatements:
        if isinstance(oStatement, If):
            for tBranch in oStatement.branches:
                yield from sequences(tBranch[1])
        elif isinstance(oStatement, Case):
            for oAlternative in oStatement.alternatives:
                yield from sequences(oAlternative.statements)
        elif isinstance(oStatement, Loop):
            yield from sequences(oStatement.statements)


def is_combinational(oProcess):
    """Returns True for a process with a sensitivity list, no wait statement and no clock edge."""
    return oProcess.sensitivity is not None and not oProcess.has_wait and not has_edge(oProcess)


def definitely_assigned(lStatements, fStatic=None):
    """
    Returns the parts of signals assigned on every path through a statement sequence, such as out1, out2(3) or r.f.
    A for loop is assumed to run, since its range is usually fixed; a while loop is not.
    fStatic(condition tokens) tells if a condition reads no signals, such as if GENERIC_G then; such a condition
    is decided at elaboration, so what any of its branches assigns counts as assigned.
    """
    setReturn = set()
    for oStatement in lStatements:
        if isinstance(oStatement, Assignment) and oStatement.kind == "signal":
            setReturn.add(oStatement.covers())
        elif isinstance(oStatement, If) and fStatic is not None and all(fStatic(t[0]) for t in oStatement.branches if t[0] is not None):
            setReturn |= set().union(*[definitely_assigned(tBranch[1], fStatic) for tBranch in oStatement.branches])
        elif isinstance(oStatement, If) and oStatement.has_else:
            setReturn |= common([definitely_assigned(tBranch[1], fStatic) for tBranch in oStatement.branches])
        elif isinstance(oStatement, Case) and oStatement.alternatives:
            setReturn |= common([definitely_assigned(o.statements, fStatic) for o in oStatement.alternatives])
        elif isinstance(oStatement, Loop) and any((o.get_value() or "").lower() == "for" for o in oStatement.header):
            setReturn |= definitely_assigned(oStatement.statements, fStatic)
    return setReturn


def common(lSets):
    """Returns the parts covered in every set, where out2 also covers out2(3)."""
    setAll = set().union(*lSets)
    return {sPart for sPart in setAll if all(covered(sPart, setParts) for setParts in lSets)}


def same_conditional_generates(tFirst, tSecond, dConditions):
    """
    Returns True if two generate contexts are in the same branches of the same if and case generate statements.
    Statements in different conditional generates may or may not both exist, which only elaboration can tell.
    """
    def conditional(tContext):
        return {(iGenerate, iBranch) for iGenerate, iBranch in tContext if iGenerate in dConditions or iBranch != 0}

    return conditional(tFirst) == conditional(tSecond)


def exclusive(tFirst, tSecond, dConditions=None):
    """
    Returns True if two generate contexts can never both be elaborated: they are in different branches of the
    same if or case generate statement, or in the first branches of two if generate statements with opposite
    conditions, such as if G generate and if not G generate.
    """
    dFirst = dict(tFirst)
    if any(iGenerate in dFirst and dFirst[iGenerate] != iBranch for iGenerate, iBranch in tSecond):
        return True
    dConditions = dConditions or {}
    lFirst = [dConditions[i] for i, b in tFirst if b == 0 and i in dConditions]
    lSecond = [dConditions[i] for i, b in tSecond if b == 0 and i in dConditions]
    return any(opposite(sFirst, sSecond) for sFirst in lFirst for sSecond in lSecond)


def opposite(sFirst, sSecond):
    """Returns True for conditions such as "g" and "not g", or "g = true" and "g = false"."""
    if sFirst == "not " + sSecond or sSecond == "not " + sFirst:
        return True
    for sTrue, sFalse in (("= true", "= false"), ("= false", "= true"), ("= '1'", "= '0'"), ("= '0'", "= '1'")):
        if sFirst.endswith(" " + sTrue) and sSecond == sFirst[: -len(sTrue)] + sFalse:
            return True
    lFirst, lSecond = sFirst.split(" "), sSecond.split(" ")
    if len(lFirst) == len(lSecond) and lFirst.count("=") + lFirst.count("/=") == 1:
        return [{"=": "/=", "/=": "="}.get(s, s) for s in lFirst] == lSecond
    return False


def covered(sPart, setParts):
    """Returns True if a part of a signal, such as out2(3) or r.f, or a prefix of it such as out2 or r, is in the set."""
    if sPart in setParts:
        return True
    for iPosition, sCharacter in enumerate(sPart):
        if sCharacter in ".(" and sPart[:iPosition] in setParts:
            return True
    return False


def overlaps(sPath, sName):
    """Returns True if a record path such as r.f and a name read such as r or r.f.g refer to overlapping data."""
    return sPath == sName or sPath.startswith(sName + ".") or sName.startswith(sPath + ".")


def is_metavalue_choice(sChoice):
    """Returns True for a string or character literal choice that contains a metavalue such as X, Z or -."""
    if len(sChoice) >= 2 and sChoice[0] in "\"'" and sChoice[-1] == sChoice[0]:
        return any(c in METAVALUES for c in sChoice[1:-1])
    return False
