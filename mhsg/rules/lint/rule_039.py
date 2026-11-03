# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule

# The declarations whose names share the name space of a design unit
OUTER = {
    ("signal_declaration", "identifier"): "signal",
    ("constant_declaration", "identifier"): "constant",
    ("interface_signal_declaration", "identifier"): "port",
    ("interface_unknown_declaration", "identifier"): "port or generic",
    ("interface_constant_declaration", "identifier"): "generic",
    ("full_type_declaration", "identifier"): "type",
    ("subtype_declaration", "identifier"): "subtype",
    ("component_declaration", "identifier"): "component",
}
# The declarations and labels that can hide an outer name
INNER = {
    ("variable_declaration", "identifier"): "variable",
    ("loop_parameter_specification", "identifier"): "loop parameter",
    ("parameter_specification", "identifier"): "loop parameter",
    ("process_statement", "process_label"): "process label",
    ("component_instantiation_statement", "instantiation_label"): "instance label",
    ("for_generate_statement", "generate_label"): "generate label",
    ("if_generate_statement", "generate_label"): "generate label",
    ("case_generate_statement", "generate_label"): "generate label",
    ("block_statement", "block_label"): "block label",
}


class rule_039(Rule):
    """
    This rule checks that names are not used twice in a design unit: a variable, loop parameter or label with the
    name of a signal, port, generic, constant, type or component of the same entity and architecture.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (DR3).

    A variable with the name of a signal hides the signal in its process, so a reader cannot tell which one a statement
    uses; a label with the name of a signal makes messages and waveforms ambiguous.

    **Violation**

    .. code-block:: vhdl

       signal count : natural range 0 to 15;
       ...
       process (all) is
         variable count : natural range 0 to 15;

    **Fix**

    .. code-block:: vhdl

       signal count : natural range 0 to 15;
       ...
       process (all) is
         variable count_v : natural range 0 to 15;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Give the object a name of its own"

    def check(self, oModel, oFile):
        dOuter = {}
        lInner = []
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            if tKind in (("entity_declaration", "identifier"), ("package_declaration", "identifier")):
                dOuter = {}
            if tKind in OUTER:
                dOuter.setdefault(oToken.get_value().lower(), OUTER[tKind])
            elif tKind in INNER:
                lInner.append((iIndex, oToken.get_value(), INNER[tKind], dict(dOuter)))
        for iIndex, sName, sKind, dNames in lInner:
            sOuter = dNames.get(sName.lower())
            if sOuter is not None:
                self.report(oFile, iIndex, f"The {sKind} {sName} has the name of a {sOuter}; give it a name of its own")
