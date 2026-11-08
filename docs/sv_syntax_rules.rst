.. include:: includes.rst

Verilog and SystemVerilog Syntax Rules
--------------------------------------

sv_syntax_001
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_syntax_error`

This rule reports code slang cannot parse. In the item of a design unit, such as a declaration or an always block,
that holds an error, the syntax tree from the line of the error to the end of the item may have constructs missing
or misplaced: the other style rules leave that part alone, and check and fix the rest of the file. For an error
outside the items of a unit, such as in its header, they leave the rest of the unit alone. The lint rules skip the
file.

A file is parsed on its own, so macros defined in other files and missing include files are not errors.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       y = a +;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       y = a + b;
   end
