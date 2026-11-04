.. include:: includes.rst

SystemVerilog Indent Rules
--------------------------

sv_indent_001
#############

|phase_4| |error| |indent|

Alias: :code:`sv_indent_code`

This rule checks the indent of SystemVerilog and Verilog code.

Each level is **indent_size** spaces, 4 by default. One level in are: the members of a module, package, interface
or class; the items of a begin-end block, a function or a task; the ports and parameters of a declaration; the
connections of an instance; the members of an enum or struct; the items of a case statement; and a statement
under if, else, a loop, an always block or a case item when it is not a begin-end block.
end, else, endmodule and the brackets closing a list are at the level of the construct they close.
A comment is indented like the next line of code, or one level more above a line closing a construct. A comment
line continuing the comment at the end of the line above, aligned with it, stays aligned with it.

Continuation lines, such as the second line of a long expression, are checked by sv_indent_002; preprocessor
directives are not checked,
nor is a file with syntax errors, whose levels may be wrong near the errors, see sv_syntax_001.

Two options follow other styles. **list_indent**, 1 by default, is the number of levels the ports and parameters
of a declaration and the connections of an instance are indented; Verible's formatter indents them by its wrap
width, which is 2 levels. **begin_style**, aligned by default, puts a begin on its own line under a control
statement at the level of the statement; indented puts it one level in, with its items one level further.

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

sv_indent_002
#############

|phase_4| |error| |indent|

Alias: :code:`sv_indent_continuation`

This rule checks that a continuation line, such as the second line of a long expression or of the arguments of a
call, is indented more than the line that starts its statement. A line that starts with a closing bracket, with the
opening bracket of a port list, with the next expression of a case item, or after an attribute on a line of its
own, may be at the level of that line.

The fix indents a continuation line like the continuation line before it in the statement, or else by
**continuation_indent** levels, 2 by default, more than the line that starts its statement, as Verible's formatter
does with its wrap width; a closing bracket goes to the level of that line.
Continuation lines indented more, such as arguments aligned after their opening bracket, are left as they are.

**Violation**

.. code-block:: systemverilog

   assign valid_o = req_i &
   ready_i;

**Fix**

.. code-block:: systemverilog

   assign valid_o = req_i &
           ready_i;
