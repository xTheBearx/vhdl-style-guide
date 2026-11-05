.. include:: includes.rst

SystemVerilog Syntax Rules
--------------------------

sv_syntax_001
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_syntax_error`

This rule reports code slang cannot parse. In the design unit, such as a module, that holds an error, the syntax
tree from the line of the first error to the end of the unit may have constructs missing or misplaced: the other
style rules leave that part alone, and check and fix the rest of the file. The lint rules skip the file.

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
