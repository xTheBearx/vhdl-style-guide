# -*- coding: utf-8 -*-

import re

from mhsg import violation
from mhsg.rule_group import whitespace
from mhsg.token import pragma

# The configured patterns for each kind of pragma
dPragmaTypes = {
    pragma.open: "open",
    pragma.close: "close",
    pragma.single: "single",
}

oDashes = re.compile(r"^--( *)(?=\S)")


class rule_100(whitespace.Rule):
    """
    This rule checks the space after the **--** of a pragma.

    .. NOTE:: This rule is disabled by default.

    The rule has an :code:`action` option:

    * :code:`add` (default): a single space after the **--**
    * :code:`remove`: no space after the **--**

    A pragma is only changed if the result still matches a pragma pattern of the same kind (open, close or single).
    For example, :code:`--vhdl_comp_off` is never changed by the default patterns, because they do not match :code:`-- vhdl_comp_off`.

    **Violation**

    .. code-block:: vhdl

       --synthesis translate_off
       --   synthesis translate_on

    **Fix**

    .. code-block:: vhdl

       -- synthesis translate_off
       -- synthesis translate_on
    """

    def __init__(self):
        super().__init__()
        self.phase = 2
        self.disable = True
        self.action = "add"
        self.configuration.append("action")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        dRegexp = oFile.configuration.dConfig["pragma"]["regexp"]
        lReturn = []
        for oToi in oFile.get_tokens_matching(list(dPragmaTypes.keys())):
            oToken = oToi.get_tokens()[0]
            sNew = self._expected_value(oToken.get_value())
            if sNew is None or sNew == oToken.get_value():
                continue
            lPatterns = dRegexp.get(dPragmaTypes[type(oToken)], [])
            if not any(oRegexp.match(sNew) for oRegexp in lPatterns):
                continue
            oToi.set_meta_data("new_value", sNew)
            lReturn.append(oToi)
        return lReturn

    def _expected_value(self, sValue):
        oMatch = oDashes.match(sValue)
        if oMatch is None:
            return None
        if self.action == "remove":
            sSpaces = ""
        else:
            sSpaces = " "
        return "--" + sSpaces + sValue[oMatch.end() :]

    def _analyze(self, lToi):
        for oToi in lToi:
            sOld = oToi.get_tokens()[0].get_value()
            sNew = oToi.get_meta_data("new_value")
            oViolation = violation.New(oToi.get_line_number(), oToi, f'Change "{sOld}" to "{sNew}"')
            oViolation.set_action({"new_value": sNew})
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        lTokens[0].set_value(oViolation.get_action()["new_value"])
        oViolation.set_tokens(lTokens)
