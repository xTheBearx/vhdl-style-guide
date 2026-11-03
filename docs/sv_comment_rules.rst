.. include:: includes.rst

SystemVerilog Comment Rules
---------------------------

sv_comment_001
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_tool_directives`

This rule checks for synthesis directives and scripts in comments, such as synopsys full_case, parallel_case
or dc_script_begin, as the STARC guide asks (2.8.1.5, 2.8.5.1, 3.1.2.7). **pattern** is the regular
expression searched for in comments. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (state_q) // synopsys full_case parallel_case

**Fix**

.. code-block:: systemverilog

   unique case (state_q)
