# -*- coding: utf-8 -*-
"""
Token classes of SystemVerilog and Verilog files.

The generic classes of mhsg.parser, such as whitespace, comment and carriage_return, are used as they are, so the
rules that only look at those work for every language. Other tokens are instances of classes made from what slang
tells about them:

* the kind of token, such as ModuleKeyword or Identifier, which selects the base class: keyword, identifier,
  preprocessor (directives and macro uses) or token;
* the syntax node the token belongs to and its field there, such as ModuleHeader and moduleKeyword.

of(syntax, field) returns the class for a syntax node and field, made the first time it is asked for, so a rule can
name exactly the tokens it is about: isinstance(oToken, tokens.of("ModuleHeader", "name")). Every token also keeps
the slang token kind and the chain of syntax nodes above it.
"""

from mhsg import parser


class token(parser.item):
    """A token of a SystemVerilog file."""

    def __init__(self, sString="", sKind="", tSyntax=(), sField=None):
        super().__init__(sString)
        # The slang token kind, such as ModuleKeyword
        self.kind = sKind
        # The syntax node kinds from the compilation unit down to the node that holds the token, without "Syntax"
        self.syntax = tSyntax
        # The field of the node that holds the token, such as moduleKeyword; None for an element of a list
        self.field = sField


class keyword(token, parser.keyword):
    """A keyword, such as module or always_ff."""


class identifier(token, parser.identifier):
    """An identifier, simple or escaped, or a system name such as $display."""


class preprocessor(token, parser.preprocessor):
    """A compiler directive, such as `define or `ifdef, or a macro use, such as `WIDTH: kept as written."""


class unclassified(token):
    """A token that is not part of the parsed code: in an inactive `ifdef branch or in the arguments of a macro."""


_dClasses = {}


def of(sSyntax, sField, oBase=token):
    """
    Returns the class of the tokens in a field of a syntax node, such as of("ModuleHeader", "name"), made the first time.
    The class derives from oBase, and the classes of one syntax node and field share one class whatever the base.
    """
    sSyntax = short_name(sSyntax)
    tKey = (sSyntax, sField)
    if tKey not in _dClasses:
        _dClasses[tKey] = type(f"{sSyntax}.{sField}", (oBase,), {"__module__": __name__})
    return _dClasses[tKey]


def for_token(sKind, tSyntax, sField):
    """Returns the class for a token: by syntax node and field when it has one, else by its kind."""
    oBase = base_class(sKind)
    if tSyntax and sField:
        oClass = of(tSyntax[-1], sField, oBase)
        if issubclass(oClass, oBase):
            return oClass
        # A field holding tokens of several kinds, such as keywords and identifiers: one class per kind
        return of(tSyntax[-1], f"{sField}.{base_name(oBase)}", oBase)
    return oBase


def base_class(sKind):
    if sKind in ("Directive", "MacroUsage", "MacroQuote", "MacroEscapedQuote", "MacroPaste", "MacroTripleQuote", "LineContinuation"):
        return preprocessor
    if sKind.endswith("Keyword"):
        return keyword
    if sKind in ("Identifier", "SystemIdentifier"):
        return identifier
    return token


def base_name(oClass):
    return oClass.__name__


def short_name(sSyntax):
    return sSyntax[: -len("Syntax")] if sSyntax.endswith("Syntax") else sSyntax
