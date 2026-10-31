# -*- coding: utf-8 -*-

from mhsg import severity
from mhsg.rules.line_length import line_length


class rule_004(line_length):
    """
    This rule checks the length of the line against a second, usually longer, limit.

    Together with :ref:`length_001` it allows staged line lengths.
    For example, length_001 can report lines over 80 characters as warnings, while this rule reports lines over 120 characters as errors.

    This rule is disabled by default.
    Its default length is 120 and its default severity is Error.

    |configuring_length_rules_link|
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.severity = severity.error("Error")
