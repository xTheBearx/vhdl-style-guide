# -*- coding: utf-8 -*-

import importlib

from mhsg import language, parser
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

# mhsg.svFile exports the class svFile under the name of its module
svFile = importlib.import_module("mhsg.svFile.svFile")

lTokens = [tokens.token, parser.comment]


class rule_001(Rule):
    """
    This rule checks the indent of SystemVerilog and Verilog code.

    Each level is **indent_size** spaces, 4 by default. One level in are: the members of a module, package, interface
    or class; the items of a begin-end block, a function or a task; the ports and parameters of a declaration; the
    connections of an instance; the members of an enum or struct; the items of a case statement; and a statement
    under if, else, a loop, an always block or a case item when it is not a begin-end block.
    end, else, endmodule and the brackets closing a list are at the level of the construct they close.
    A comment is indented like the next line of code, or one level more above a line closing a construct. A comment
    line continuing the comment at the end of the line above, aligned with it, stays aligned with it.

    Continuation lines, such as the second line of a long expression, and preprocessor directives are not checked.

    **Violation**

    .. code-block:: systemverilog

       module counter (
       input logic clk_i
       );
         always_ff @(posedge clk_i) begin
         count_q <= count_d;
           end
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module counter (
           input logic clk_i
       );
           always_ff @(posedge clk_i) begin
               count_q <= count_d;
           end
       endmodule
    """

    def __init__(self):
        super().__init__(lTokens)
        self.languages = (language.SYSTEMVERILOG,)

    def fix(self, oFile, dFixOnly=None):
        super().fix(oFile, dFixOnly)
        # A comment continuing a trailing comment moves with it
        if self.fixable and svFile.realign_comment_continuations(oFile.lAllObjects):
            oFile.update_token_map()
