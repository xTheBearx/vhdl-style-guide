# -*- coding: utf-8 -*-

from mhsg.rules.move_token_next_to_another_token import move_token_next_to_another_token
from mhsg.token import subprogram_instantiation_declaration as token


class rule_004(move_token_next_to_another_token):
    """
    This rule checks the **new** keyword is on the same line as the **is** keyword.

    **Violation**

    .. code-block:: vhdl

       procedure my_proc is
       new my_generic_proc

    **Fix**

    .. code-block:: vhdl

       procedure my_proc is new my_generic_proc
    """

    def __init__(self):
        super().__init__(token.is_keyword, token.new_keyword)
        self.solution = "Ensure the *new* keyword is on the same line as the *is* keyword."
