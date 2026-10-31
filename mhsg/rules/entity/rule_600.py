# -*- coding: utf-8 -*-

from mhsg import parser, token
from mhsg.rules.consistent_token_case import consistent_token_case as Rule

lTokens = []
lTokens.append(token.interface_unknown_declaration.identifier)
lTokens.append(token.interface_constant_declaration.identifier)
lTokens.append(token.interface_variable_declaration.identifier)
lTokens.append(token.interface_signal_declaration.identifier)

lNames = []
lNames.append(parser.todo)
lNames.append(token.todo.name)


class rule_600(Rule):
    """
    This rule checks for consistent capitalization of generic names in entity declarations.

    **Violation**

    .. code-block:: vhdl

       entity FIFO is
         generic (
           G_WIDTH : natural := 16
         );
         port (
           I_DATA : std_logic_vector(g_width - 1 downto 0);
           O_DATA : std_logic_vector(g_width - 1 downto 0)
         );
       end entity fifo;

    **Fix**

    .. code-block:: vhdl

       entity FIFO is
         generic (
           G_WIDTH : natural := 16
         );
         port (
           I_DATA : std_logic_vector(G_WIDTH - 1 downto 0);
           O_DATA : std_logic_vector(G_WIDTH - 1 downto 0)
         );
       end entity fifo;
    """

    def __init__(self):
        super().__init__(lTokens, lNames)
        self.bNamesInDeclaringScopeOnly = True
        self.lDeclarationKinds = ["generic"]
        self.lDeclarationScopes = ["entity"]
