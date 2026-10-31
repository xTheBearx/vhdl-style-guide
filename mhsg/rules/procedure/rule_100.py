# -*- coding: utf-8 -*-

from mhsg import deprecated_rule


class rule_100(deprecated_rule.Rule):
    """
    This rule has been split into the following rules:

    * :ref:`procedure_102`
    * :ref:`procedure_103`
    * :ref:`procedure_104`
    """

    def __init__(self):
        super().__init__()
        self.message.append("Rule " + self.unique_id + " has been split into the following rules:")
        self.message.append("  procedure_102")
        self.message.append("  procedure_103")
        self.message.append("  procedure_104")
