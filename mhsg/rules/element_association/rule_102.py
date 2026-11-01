# -*- coding: utf-8 -*-

from mhsg.rules.whitespace_before_token import Rule
from mhsg.token import choice, element_association


class rule_102(Rule):
    """
    This rule checks for at least a single space before the => in an element_association.

    Arguments of a function call nested in another call, such as :code:`get(arr => x)`, are element associations as well.
    The space between **others** and => is checked by rule element_association_100.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       a <= (enable=> '1', data=> x"00");

    **Fix**

    .. code-block:: vhdl

       a <= (enable => '1', data => x"00");
    """

    def __init__(self):
        super().__init__([element_association.assignment])
        self.number_of_spaces = ">=1"

    def _get_tokens_of_interest(self, oFile):
        return [oToi for oToi in super()._get_tokens_of_interest(oFile) if not follows_others(oToi)]


def follows_others(oToi):
    return any(isinstance(oToken, choice.others_keyword) for oToken in oToi.get_tokens()[:-1])
