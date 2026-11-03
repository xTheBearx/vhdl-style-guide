# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_036(Rule):
    """
    This rule checks the bodies of functions and procedures: a function returns a value on every path, and no
    subprogram waits.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (CP9).

    A function that can reach its end without a return statement fails in simulation only when that path is taken,
    and synthesis tools treat it differently. A wait statement in a procedure cannot be synthesized.

    **Violation**

    .. code-block:: vhdl

       function parity(data : std_logic_vector) return std_logic is
       begin
         if data'length > 0 then
           return xor data;
         end if;
       end function parity;

    **Fix**

    .. code-block:: vhdl

       function parity(data : std_logic_vector) return std_logic is
       begin
         if data'length > 0 then
           return xor data;
         end if;
         return '0';
       end function parity;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Return a value on every path"

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        lStack = []
        for iIndex, oToken in enumerate(lTokens):
            tKind = model.kind(oToken)
            if tKind in (("function_specification", "function_keyword"), ("procedure_specification", "procedure_keyword")):
                lStack.append({"kind": tKind[0].split("_")[0], "name": None, "index": iIndex})
            elif tKind in (("function_specification", "designator"), ("procedure_specification", "designator")) and lStack and lStack[-1]["name"] is None:
                lStack[-1]["name"] = oToken.get_value()
                lStack[-1]["index"] = iIndex
            elif tKind == ("subprogram_declaration", "semicolon") and lStack:
                lStack.pop()
            elif tKind == ("subprogram_body", "begin_keyword") and lStack:
                dSubprogram = lStack[-1]
                lStatements, _ = oModel._sequence(iIndex + 1, {("subprogram_body", "end_keyword")})  # pylint: disable=protected-access
                for oStatement in model.walk(lStatements):
                    if isinstance(oStatement, model.Other) and oStatement.kind == "wait":
                        self.report(
                            oFile,
                            oStatement.index,
                            f"Remove the wait statement from {dSubprogram['kind']} {dSubprogram['name']}; synthesis does not support it",
                        )
                if dSubprogram["kind"] == "function" and not returns(lTokens, lStatements):
                    self.report(oFile, dSubprogram["index"], f"Function {dSubprogram['name']} can reach its end without returning a value")
            elif tKind == ("subprogram_body", "end_keyword") and lStack:
                lStack.pop()


def returns(lTokens, lStatements):
    """Returns whether a statement list returns on every path."""
    for oStatement in lStatements:
        if isinstance(oStatement, model.Other) and model.kind(lTokens[oStatement.index])[0] == "return_statement":
            return True
        if isinstance(oStatement, model.If) and oStatement.has_else and all(returns(lTokens, t[1]) for t in oStatement.branches):
            return True
        if isinstance(oStatement, model.Case) and oStatement.alternatives and all(returns(lTokens, o.statements) for o in oStatement.alternatives):
            return True
    return False
