# -*- coding: utf-8 -*-

from mhsg import deprecated_rule


class rule_504(deprecated_rule.Rule):
    """
    This rule duplicated :ref:`procedure_008`, which checks the case of the **end** keyword in procedure bodies.
    """

    def __init__(self):
        super().__init__()
        self.message.append("Rule " + self.unique_id + " duplicated rule procedure_008, which checks the case of the end keyword in procedure bodies.")
        self.message.append("Configure procedure_008 instead.")
