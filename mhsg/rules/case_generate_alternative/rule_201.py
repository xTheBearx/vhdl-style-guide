# -*- coding: utf-8 -*-

from mhsg.rules.previous_line import previous_line as Rule
from mhsg.token import case_generate_alternative as token


class rule_201(Rule):
    """
    This rule checks for blank lines or comments above the **when** keyword.

    |configuring_previous_line_rules_link|

    The default style is :code:`allow_comment`.

    **Violation**

    .. code-block:: vhdl

       case data is
         when 3 =>
         -- Comment
         when 4 =>

    **Fix**

    .. code-block:: vhdl

       case data is

         when 3 =>

         -- Comment
         when 4 =>
    """

    def __init__(self):
        super().__init__([token.when_keyword])
        self.style = "allow_comment"
