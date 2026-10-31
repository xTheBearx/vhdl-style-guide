# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.token_indent_unless_between_tokens import (
    token_indent_unless_between_tokens,
)
from mhsg.token import (
    concurrent_conditional_signal_assignment,
    conditional_variable_assignment,
    conditional_waveform_assignment,
    constant_declaration,
)

lTokens = []
lTokens.append(parser.comment)

lUnless = []
lUnless.append([constant_declaration.constant_keyword, constant_declaration.semicolon])
# Comments inside conditional assignments are aligned with the code around them by concurrent_009, sequential_401 and variable_assignment_400
lUnless.append([concurrent_conditional_signal_assignment.assignment, concurrent_conditional_signal_assignment.semicolon])
lUnless.append([conditional_waveform_assignment.assignment, conditional_waveform_assignment.semicolon])
lUnless.append([conditional_variable_assignment.assignment, conditional_variable_assignment.semicolon])


class rule_010(token_indent_unless_between_tokens):
    """
    This rule checks the indent lines starting with comments.

    Comments inside multiline conditional assignments are not checked by this rule.
    They are aligned with the code around them by rules :ref:`concurrent_009`, :ref:`sequential_401` and :ref:`variable_assignment_400`.

    |configuring_comment_indenting_link|

    **Violation**

    .. code-block:: vhdl

           -- Libraries
       library ieee;

        -- Define architecture
       architecture rtl of fifo is

       -- Define signals
         signal wr_en : std_logic;
         signal rd_en : std_Logic;

       begin

    **Fix**

    .. code-block:: vhdl

       -- Libraries
       library ieee;

       -- Define architecture
       architecture rtl of fifo is

         -- Define signals
         signal wr_en : std_logic;
         signal rd_en : std_Logic;

       begin
    """

    def __init__(self):
        super().__init__(lTokens, lUnless)
        self.phase = 4
        self.subphase = 3
