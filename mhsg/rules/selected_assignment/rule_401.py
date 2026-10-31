# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.align_tokens_in_region_between_tokens import (
    align_tokens_in_region_between_tokens as Rule,
)
from mhsg.vhdlFile import utils

lAlign = []
lAlign.append(token.selected_waveforms.when_keyword)
lAlign.append(token.selected_expressions.when_keyword)

lTokenPairs = []
lTokenPairs.append([token.concurrent_selected_signal_assignment.with_keyword, token.concurrent_selected_signal_assignment.semicolon])
lTokenPairs.append([token.selected_force_assignment.with_keyword, token.selected_force_assignment.semicolon])
lTokenPairs.append([token.selected_variable_assignment.with_keyword, token.selected_variable_assignment.semicolon])
lTokenPairs.append([token.selected_waveform_assignment.with_keyword, token.selected_waveform_assignment.semicolon])


class rule_401(Rule):
    """
    This rule checks the **when** keywords are aligned in selected assignments.

    .. NOTE:: This rule conflicts with selected_assignment_106, which requires a single space before **when**.
       Set :code:`number_of_spaces` of selected_assignment_106 to :code:`'>=1'` when enabling this rule.

    |configuring_keyword_alignment_rules_link|

    **Violation**

    .. code-block:: vhdl

       with my_expression select my_output <=
         c_first when 1,
         c_second when 2,
         (others => '0') when others;

    **Fix**

    .. code-block:: vhdl

       with my_expression select my_output <=
         c_first         when 1,
         c_second        when 2,
         (others => '0') when others;
    """

    def __init__(self):
        super().__init__(lAlign, None, None)
        self.solution = "Align when keywords."
        self.disable = True
        self.compact_alignment = "yes"
        self.blank_line_ends_group = "no"
        self.comment_line_ends_group = "no"
        self.separate_generic_port_alignment = "no"
        self.configuration.remove("separate_generic_port_alignment")
        self.configuration.remove("case_control_statements_ends_group")
        self.configuration.remove("if_control_statements_ends_group")
        self.configuration.remove("loop_control_statements_ends_group")

    def _get_tokens_of_interest(self, oFile):
        lToi = []
        for lTokenPair in lTokenPairs:
            aToi = oFile.get_tokens_bounded_by(lTokenPair[0], lTokenPair[1], bIncludeTillBeginningOfLine=True)
            lToi = utils.combine_two_token_class_lists(lToi, aToi)
        return lToi
