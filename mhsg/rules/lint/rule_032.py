# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_032(Rule):
    """
    This rule checks that every deferred constant of a package gets its value in the package body of the same file.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS7).

    A deferred constant is declared in a package without a value; the package body gives it one. If the body is in
    another file, or leaves it out, the value is hard to find in a review, and a body that leaves it out does not
    compile. Keep the package and its body in one file, or give the constant its value in the package.

    **Violation**

    .. code-block:: vhdl

       package config_pkg is
         constant c_depth : natural;
       end package config_pkg;

    **Fix**

    .. code-block:: vhdl

       package config_pkg is
         constant c_depth : natural := 16;
       end package config_pkg;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Give the deferred constant its value"

    def check(self, oModel, oFile):
        dDeferred = {}
        dDefined = {}
        sPackage = None
        bBody = False
        lNames = []
        bValue = False
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            tKind = model.kind(oToken)
            if tKind == ("package_declaration", "identifier"):
                sPackage, bBody = oToken.get_value().lower(), False
            elif tKind == ("package_body", "package_simple_name"):
                sPackage, bBody = oToken.get_value().lower(), True
            elif tKind in (("package_declaration", "end_keyword"), ("package_body", "end_keyword")):
                sPackage = None
            elif sPackage is None:
                continue
            elif tKind == ("constant_declaration", "identifier"):
                lNames.append((oToken.get_value().lower(), iIndex, oToken.get_value()))
            elif tKind == ("constant_declaration", "assignment_operator"):
                bValue = True
            elif tKind == ("constant_declaration", "semicolon"):
                for sName, iName, sText in lNames:
                    if bBody and bValue:
                        dDefined.setdefault(sPackage, set()).add(sName)
                    elif not bBody and not bValue:
                        dDeferred.setdefault(sPackage, []).append((sName, iName, sText))
                lNames, bValue = [], False
        for sPackage, lConstants in dDeferred.items():
            for sName, iIndex, sText in lConstants:
                if sName not in dDefined.get(sPackage, set()):
                    self.report(oFile, iIndex, f"Give deferred constant {sText} its value in the package body of this file, or in the package")
