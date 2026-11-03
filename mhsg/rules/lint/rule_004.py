# -*- coding: utf-8 -*-

from mhsg.rules.lint.rule_003 import rule_003 as Rule


class rule_004(Rule):
    """
    This rule checks that every output port of an instance is connected.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP12.

    An output, buffer or inout port that is missing from the port map, or mapped to :code:`open`, is not used.
    That is sometimes intended, for example for a debug output, and should then be justified.
    The ports of the instantiated unit are taken from the file or from the other files of the run.

    **Violation**

    .. code-block:: vhdl

       u_bad : usable_vhd
         port map (
           in1  => d,
           in2  => addr,
           out1 => open,
           out2 => q
         );

    **Fix**

    .. code-block:: vhdl

       u_bad : usable_vhd
         port map (
           in1  => d,
           in2  => addr,
           out1 => q1,
           out2 => q
         );
    """

    lModes = ("out", "buffer")
    sKind = "Output"

    def __init__(self):
        super().__init__()
        self.solution = "Connect the output port"
