.. include:: includes.rst

SystemVerilog Syntax Rules
--------------------------

sv_syntax_001
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_syntax_error`

This rule reports code slang cannot parse. The rules on constructs, such as always blocks and labels, skip a file
with syntax errors, as its syntax tree has constructs missing or misplaced.

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
