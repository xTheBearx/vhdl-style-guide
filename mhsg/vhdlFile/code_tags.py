# -*- coding: utf-8 -*-

from mhsg import parser, rule_aliases
from mhsg.token import delimited_comment


class New:
    def __init__(self):
        self.code_tags = []
        self.next_line_code_tags = []
        self.bIgnoreNextCarriageReturn = False

    def clear(self):
        self.code_tags.clear()
        self.next_line_code_tags.clear()

    def clear_next_line_code_tags(self):
        self.next_line_code_tags.clear()

    def remove(self, sCodeTag):
        if sCodeTag in self.code_tags:
            self.code_tags.remove(sCodeTag)

    def add(self, sCodeTag):
        if sCodeTag not in self.code_tags:
            self.code_tags.append(sCodeTag)

    def get_tags(self):
        lReturn = []
        lReturn.extend(self.code_tags)
        lReturn.extend(self.next_line_code_tags)
        return lReturn

    def update(self, oToken):
        if isinstance(oToken, parser.carriage_return):
            if self.bIgnoreNextCarriageReturn:
                self.bIgnoreNextCarriageReturn = False
            else:
                self.next_line_code_tags.clear()
            return None

        if on_code_tag_detected(oToken):
            remove_code_tags(self, oToken)
            return False
        elif off_code_tag_detected(oToken):
            add_code_tags(self, oToken)
            return True
        elif next_line_code_tag_detected(oToken):
            add_next_line_code_tags(self, oToken)
            self.bIgnoreNextCarriageReturn = True


def on_code_tag_detected(oToken):
    if not isinstance(oToken, parser.comment):
        return False
    if token_starts_with(oToken, ("-- mhsg_on", "-- vsg_on", "// mhsg_on")):
        return True
    return False


def off_code_tag_detected(oToken):
    if not isinstance(oToken, parser.comment):
        return False
    if token_starts_with(oToken, ("-- mhsg_off", "-- vsg_off", "// mhsg_off")):
        return True
    return False


def next_line_code_tag_detected(oToken):
    if not isinstance(oToken, parser.comment):
        return False
    if token_starts_with(oToken, ("-- mhsg_disable_next_line", "-- vsg_disable_next_line", "// mhsg_disable_next_line")):
        return True
    return False


def token_starts_with(oToken, sString):
    if comment_value(oToken).startswith(sString):
        return True
    return False


def tag_comment(lTokens, iToken):
    """
    The comment token code tags are read from. VHDL splits a delimited comment into /*, its text and */; the text of
    one on a single line is read as the line comment // text.
    """
    oToken = lTokens[iToken]
    if (
        isinstance(oToken, delimited_comment.text)
        and 0 < iToken < len(lTokens) - 1
        and isinstance(lTokens[iToken - 1], delimited_comment.beginning)
        and isinstance(lTokens[iToken + 1], delimited_comment.ending)
    ):
        return parser.comment("// " + oToken.get_value().strip())
    return oToken


def comment_value(oToken):
    """
    The text of a comment, with a block comment on one line read as a line comment: /* mhsg_off */ reads as
    // mhsg_off, so code tags can be written either way.
    """
    sValue = oToken.get_value()
    if sValue.startswith("/* ") and sValue.endswith("*/") and "\n" not in sValue:
        return "// " + sValue[3:-2].strip()
    return sValue


def remove_code_tags(self, oToken):
    sValue = remove_code_tag_comment(oToken)
    lValues = sValue.split()
    if bare_code_tag(lValues):
        self.clear()
    else:
        for sCodeTag in lValues[2:]:
            self.remove(rule_aliases.get_rule_id(sCodeTag))


def add_code_tags(self, oToken):
    sValue = remove_code_tag_comment(oToken)
    lValues = sValue.split()
    if bare_code_tag(lValues):
        self.clear()
        self.add("all")
    else:
        for sCodeTag in lValues[2:]:
            self.add(rule_aliases.get_rule_id(sCodeTag))


def remove_code_tag_comment(oToken):
    lString = comment_value(oToken).split(":")
    return lString[0]


def add_next_line_code_tags(self, oToken):
    sValue = remove_code_tag_comment(oToken)
    lValues = sValue.split()
    for sCodeTag in lValues[2:]:
        sCodeTag = rule_aliases.get_rule_id(sCodeTag)
        if sCodeTag not in self.next_line_code_tags:
            self.next_line_code_tags.append(sCodeTag)


def bare_code_tag(lValues):
    if len(lValues) == 2:
        return True
    return False


def token_has_mhsg_on_code_tag(oToken):
    return on_code_tag_detected(oToken)


def token_has_mhsg_off_code_tag(oToken):
    return off_code_tag_detected(oToken)


def token_has_next_line_code_tag(oToken):
    return next_line_code_tag_detected(oToken)


def line_has_bare_off_code_tag(sLine):
    return _line_has_bare_code_tag(sLine, ("-- mhsg_off", "-- vsg_off"))


def line_has_bare_on_code_tag(sLine):
    return _line_has_bare_code_tag(sLine, ("-- mhsg_on", "-- vsg_on"))


def file_has_bare_off_code_tag(lLines):
    return any(line_has_bare_off_code_tag(sLine) for sLine in lLines)


def _line_has_bare_code_tag(sLine, tTags):
    """
    A bare code tag names no rules, so it turns every rule off or on. Text after a colon is a comment.
    """
    sValue = sLine.strip()
    if not sValue.startswith(tTags):
        return False
    return len(sValue.split(":")[0].split()) == 2
