# -*- coding: utf-8 -*-

import re

from mhsg.lint import model
from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_034 import statement_tokens

reBits = re.compile(r'^([0-9]*[uUsS]?[bBoOxXdD])?"([^"]*)"$')


class rule_035(Rule):
    """
    This rule checks for vector values written as bit strings in statements, other than all zeros and all ones.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (CP4).

    A value such as "0110" or x"A5" says nothing of what it stands for, and its width must change with the vector.
    Declare a constant with a name, or build the value from named constants. All zeros and all ones, written
    as bit strings or as (others => '0'), are not reported.

    **Violation**

    .. code-block:: vhdl

       command <= "0110";

    **Fix**

    .. code-block:: vhdl

       constant c_read_command : std_logic_vector(3 downto 0) := "0110";
       ...
       command <= c_read_command;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a named constant"

    def check(self, oModel, oFile):
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        lReported = []
        for lTokens in statement_tokens(oModel, oFile):
            for iPosition, oToken in enumerate(lTokens):
                sValue = oToken.get_value() or ""
                oMatch = reBits.match(sValue)
                if oMatch is None or id(oToken) in lReported:
                    continue
                sDigits = oMatch.group(2).replace("_", "")
                # A bit string literal with a base, such as x"A5", is a base token and a value token
                bBase = bool(oMatch.group(1)) or model.kind(oToken) == ("bit_string_literal", "bit_value_string")
                if model.kind(oToken) == ("bit_string_literal", "bit_value_string") and iPosition > 0:
                    sValue = (lTokens[iPosition - 1].get_value() or "") + sValue
                if len(sDigits) < 2 and not bBase:
                    continue
                if not bBase and not set(sDigits) <= set("01xXzZuUwWlLhH-"):
                    continue
                if len(set(sDigits.lower())) <= 1 and sDigits[:1].lower() in ("0", "1", "f") and (sDigits[:1] != "f" or bBase):
                    continue
                lReported.append(id(oToken))
                self.report(oFile, dIndexes[id(oToken)], f"Replace {sValue} by a named constant")
