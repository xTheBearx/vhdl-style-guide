# -*- coding: utf-8 -*-

from mhsg import deprecated_rule


class rule_006(deprecated_rule.Rule):
    """
    This rule has been replaced by :ref:`if_200`, which supports the **style** option.
    """

    def __init__(self):
        super().__init__()
        self.message.append("Rule " + self.unique_id + " has been replaced by rule if_200, which supports the style option.")
