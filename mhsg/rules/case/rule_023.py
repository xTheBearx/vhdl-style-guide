# -*- coding: utf-8 -*-

from mhsg import rule, violation
from mhsg.lint.model import is_trivia, kind
from mhsg.vhdlFile.extract import tokens


class rule_023(rule.Rule):
    """
    This rule checks that the end of a case statement repeats its label.

    .. NOTE:: This rule is disabled by default.

    A case statement without a label is reported by case_022 instead.
    It is the opposite of case_020, which removes the label after **end case**, so enable only one of them.

    **Violation**

    .. code-block:: vhdl

       address_decode : case address is
         when others => null;
       end case;

    **Fix**

    .. code-block:: vhdl

       address_decode : case address is
         when others => null;
       end case address_decode;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add the label after end case"
        self.phase = 1
        self.disable = True
        self.fixable = False
        self.groups.append("structure")

    def analyze(self, oFile):
        self._print_debug_message("Analyzing rule: " + self.unique_id)
        lTokens = oFile.lAllObjects
        lLabels = []
        for iIndex, oToken in enumerate(lTokens):
            tKind = kind(oToken)
            if tKind == ("case_statement", "case_keyword"):
                lLabels.append(find_label(lTokens, iIndex))
            elif tKind == ("case_statement", "end_case_keyword"):
                sLabel = lLabels.pop() if lLabels else None
                iNext = iIndex + 1
                while iNext < len(lTokens) and is_trivia(lTokens[iNext]):
                    iNext += 1
                if sLabel is not None and (iNext >= len(lTokens) or kind(lTokens[iNext]) != ("case_statement", "end_case_label")):
                    iLine = oFile.get_token_map().get_line_number_of_index(iIndex)
                    self.add_violation(violation.New(iLine, tokens.New(iIndex, iLine, [oToken]), "Add " + sLabel + " after end case"))


def find_label(lTokens, iIndex):
    """Returns the label of the case statement whose case keyword is at iIndex, or None."""
    for iPrevious in range(iIndex - 1, -1, -1):
        tKind = kind(lTokens[iPrevious])
        if tKind == ("case_statement", "case_label"):
            return lTokens[iPrevious].get_value()
        if not is_trivia(lTokens[iPrevious]) and tKind != ("case_statement", "label_colon"):
            return None
    return None
