# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule

PORT_IDENTIFIERS = (("interface_signal_declaration", "identifier"), ("interface_unknown_declaration", "identifier"))


class rule_013(Rule):
    """
    This rule checks for initial values on signals and output ports.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS16.

    Registers should get their value from an explicit reset, not from an initial value, so that uninitialized values show up in simulation.
    Initial values of input ports are defaults for unconnected inputs and are not reported; see lint_003.

    **Violation**

    .. code-block:: vhdl

       signal count : unsigned(3 downto 0) := (others => '0');

    **Fix**

    .. code-block:: vhdl

       signal count : unsigned(3 downto 0);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the initial value"

    def check(self, oModel, oFile):
        lNames = []
        sMode = "in"
        bPortClause = False
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            if tKind == ("port_clause", "port_keyword"):
                bPortClause = True
            elif tKind == ("port_clause", "close_parenthesis"):
                bPortClause = False
            elif tKind == ("signal_declaration", "identifier") or (bPortClause and tKind in PORT_IDENTIFIERS):
                lNames.append(oToken.get_value())
            elif bPortClause and tKind[0] == "mode":
                sMode = oToken.get_value().lower()
            elif tKind == ("signal_declaration", "assignment_operator"):
                self.report(oFile, iIndex, f"Remove the initial value of signal {', '.join(lNames)}")
            elif bPortClause and tKind == ("simple_mode_indication", "assignment") and sMode in ("out", "inout", "buffer"):
                self.report(oFile, iIndex, f"Remove the initial value of port {', '.join(lNames)}")
            if isinstance(oToken, model.parser.semicolon) or tKind == ("port_clause", "close_parenthesis"):
                lNames = []
                sMode = "in"
