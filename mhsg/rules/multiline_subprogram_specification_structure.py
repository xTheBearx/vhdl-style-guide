# -*- coding: utf-8 -*-

from mhsg import parser, token
from mhsg.rule_group import structure
from mhsg.rules import check, fix, utils as rules_utils
from mhsg.vhdlFile import utils


class multiline_subprogram_specification_structure(structure.Rule):
    """
    This rule checks the structure of multiline subprogram specifications.
    """

    def __init__(self):
        super().__init__()
        self.phase = 1
        self.lTokenPairs = None
        self.configuration_documentation_link = "configuring_subprogram_specification_statement_rules_link"
        self.oSubprogramSpecification = None

        self.first_open_paren = "remove_new_line"
        self.configuration.append("first_open_paren")
        self.last_close_paren = "add_new_line"
        self.configuration.append("last_close_paren")
        self.interface_list_semicolon = "remove_new_line"
        self.configuration.append("interface_list_semicolon")
        self.interface_element = "add_new_line"
        self.configuration.append("interface_element")
        self.ignore_single_line = "no"
        self.configuration.append("ignore_single_line")

    def _get_tokens_of_interest(self, oFile):
        # Include the rest of the closing line, so a fix that joins lines can move a comment past it
        lToi = []
        for lTokenPair in self.lTokenPairs:
            for oToi in oFile.get_tokens_bounded_by(lTokenPair[0], lTokenPair[1], bIncludeTillEndOfLine=True):
                lTokens = oToi.get_tokens()
                if isinstance(lTokens[-1], parser.carriage_return):
                    oToi = oToi.extract_tokens(0, len(lTokens) - 2)
                lToi.append(oToi)
        return lToi

    def _analyze(self, lToi):
        for oToi in lToi:
            if rules_utils.is_single_line(oToi) and utils.convert_yes_no_option_to_boolean(self.ignore_single_line):
                continue

            _check_first_open_paren(self, oToi)
            _check_last_close_paren(self, oToi)
            _check_interface_list_semicolon(self, oToi)
            _check_interface_element(self, oToi)

        self._sort_violations()

    def _fix_violation(self, oViolation):
        fix.fix_violation(oViolation)


def _check_first_open_paren(self, oToi):
    check.add_new_line_and_remove_new_line(self, oToi, self.first_open_paren, self.oSubprogramSpecification.open_parenthesis)


def _check_last_close_paren(self, oToi):
    check.add_new_line_and_remove_new_line(self, oToi, self.last_close_paren, self.oSubprogramSpecification.close_parenthesis)


def _check_interface_list_semicolon(self, oToi):
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_list_semicolon, token.interface_list.semicolon)


def _check_interface_element(self, oToi):
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_element, token.interface_unknown_declaration.identifier)
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_element, token.interface_constant_declaration.constant_keyword)
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_element, token.interface_signal_declaration.signal_keyword)
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_element, token.interface_variable_declaration.variable_keyword)
    check.add_new_line_and_remove_new_line(self, oToi, self.interface_element, token.interface_file_declaration.file_keyword)
