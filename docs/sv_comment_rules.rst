.. include:: includes.rst

SystemVerilog Comment Rules
---------------------------

sv_comment_001
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_tool_directives`

This rule checks for synthesis directives and scripts in comments, such as synopsys full_case, parallel_case
or dc_script_begin, the set and reset directives such as sync_set_reset, and implementation directives, as the
STARC guide asks (2.8.1.5, 2.8.5.1, 3.1.2.7, 1.3.1.5, 5.6.2). **pattern** is the regular
expression searched for in comments. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (state_q) // synopsys full_case parallel_case

**Fix**

.. code-block:: systemverilog

   unique case (state_q)

sv_comment_002
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_line_comments`

This rule checks that comments are line comments, starting with //, not block comments between /* and */, as the
STARC guide asks (3.5.6.7). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   /* The width of the data */
   localparam int Width = 8;

**Fix**

.. code-block:: systemverilog

   // The width of the data
   localparam int Width = 8;

sv_comment_003
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_file_header`

This rule checks that a file starts with a header comment giving each of **header_fields**, regular expressions
matched ignoring case, by default the module or circuit name, its function, the author and the date, as the STARC
guide recommends (3.5.3.1). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo (input logic clk_i);

**Fix**

.. code-block:: systemverilog

   // Module:   fifo
   // Function: first in, first out buffer
   // Author:   A. Designer
   // Date:     2026-11-04
   module fifo (input logic clk_i);
