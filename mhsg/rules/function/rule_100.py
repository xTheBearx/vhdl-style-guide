# -*- coding: utf-8 -*-

from mhsg import deprecated_rule


class rule_100(deprecated_rule.Rule):
    """
    This rule has been split into the following rules:

    * :ref:`function_102`
    * :ref:`function_103`
    * :ref:`function_104`
    * :ref:`function_105`
    * :ref:`function_106`
    * :ref:`function_107`
    """

    def __init__(self):
        super().__init__()
        self.message.append("Rule " + self.unique_id + " has been split into the following rules:")
        self.message.append("  function_102")
        self.message.append("  function_103")
        self.message.append("  function_104")
        self.message.append("  function_105")
        self.message.append("  function_106")
        self.message.append("  function_107")
