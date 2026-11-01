# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_before_tokens_in_between_tokens import Rule

lTokens = []
lTokens.append(token.association_element.assignment)

oStart = token.procedure_call.open_parenthesis
oEnd = token.procedure_call.close_parenthesis


class rule_102(Rule):
    """
    This rule checks for at least a single space before the **=>** operator in procedure calls.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       connect_ports(port_1=> data, port_2=> enable);

    **Fix**

    .. code-block:: vhdl

       connect_ports(port_1 => data, port_2 => enable);
    """

    def __init__(self):
        super().__init__(lTokens, oStart, oEnd)
        self.number_of_spaces = ">=1"
