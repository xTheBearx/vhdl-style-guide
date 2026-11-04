.. include:: includes.rst

SystemVerilog Syntax Rules
--------------------------

sv_syntax_001
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_syntax_error`

This rule reports code slang cannot parse. The other style rules check only the code before the first error,
as the syntax tree after it may have constructs missing or misplaced, and fix nothing in the file; the lint rules
skip the file.

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
