.. include:: includes.rst

Verilog and SystemVerilog Comment Rules
---------------------------------------

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

This rule checks that comments are line comments, starting with :code:`//`, not block comments between :code:`/*`
and :code:`*/`, as the STARC guide asks (3.5.6.7). It is disabled by default; the starc rule set enables it.

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

sv_comment_004
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_declarations`

This rule checks that each port and each signal of a module is declared with a comment, at the end of its line or
on the line before, as the STARC guide recommends (3.5.6.3). It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   logic [7:0] count;

**Fix**

.. code-block:: systemverilog

   logic [7:0] count;  // words in the buffer

sv_comment_005
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_ascii`

This rule checks that comments hold only ASCII characters, as the STARC guide recommends (3.5.6.4, 3.5.6.5):
write comments in English, as some tools cannot read other characters. It is disabled by default; the starc rule
set enables it.

**Violation**

.. code-block:: systemverilog

   // Zähler

**Fix**

.. code-block:: systemverilog

   // counter

sv_comment_006
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_header_history`

This rule checks that the header comment at the start of a file records its changes, matching each of
**history_fields**, regular expressions matched ignoring case, by default a word such as modified, history or
revision, as the STARC guide recommends (3.5.3.2) for code that is reused. sv_comment_003 checks the other fields
of the header. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   // Module: fifo, Author: A. Designer, Date: 2026-11-04

**Fix**

.. code-block:: systemverilog

   // Module: fifo, Author: A. Designer, Date: 2026-11-04
   // History: 2026-11-05 B. Reviewer, deeper buffer

sv_comment_007
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_density`

This rule checks that at least **minimum_comment_percent** percent of the lines of a module, 10 by default, have
a comment, as the STARC guide recommends (3.5.6.1). Modules of fewer than 10 lines are not checked. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo (...);  // 200 lines, 3 comments

**Fix**

Describe the ports, signals and blocks of the module in comments.

sv_comment_008
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_commented_out_code`

This rule checks for comments which contain commented-out code. A line comment on a line of its own is reported
if it ends like a statement or declaration, with a semicolon or a keyword such as begin, end or else, it parses as
SystemVerilog, as a module item or a statement, and its words are keywords or names used in the code of the file;
with a symbol of code, such as =, <= or (, half of its words are enough, as commented-out code can name what was
removed. Comments written as sentences do not parse, and directives of tools, such as synopsys or verilator
comments, are not reported. It is disabled by default; the do254_plus rule set enables it (DEAD).

.. NOTE:: This rule only reports the comments: deciding whether to delete them is left to the user.

**Violation**

.. code-block:: systemverilog

   // Wait for the FIFO to empty
   // if (rd_en) data_q <= data_d;
   if (empty) data_q <= '0;

**Fix**

.. code-block:: systemverilog

   // Wait for the FIFO to empty
   if (empty) data_q <= '0;

sv_comment_009
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_hidden_region`

This rule checks for regions of code hidden from synthesis or from coverage. It is disabled by default; the
do254_plus rule set enables it (PRAGMA).

Code between // synopsys translate_off and translate_on, or under an ifndef SYNTHESIS directive, is simulated but not
synthesized, and code between // coverage off and coverage on is not counted in coverage. Each such region should
be justified, with a waiver that gives the reason.

**Violation**

.. code-block:: systemverilog

   // synopsys translate_off
   initial $display("width %0d", Width);
   // synopsys translate_on

sv_comment_010
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_comment_requirement_tag`

This rule checks that modules and always blocks carry a requirement tag, for traceability to the hardware
requirements. It is disabled by default; the do254_plus rule set enables it (REQ).

One of the comment lines directly above the module or always block, or the first comment inside it, must match
the **pattern** option, a regular expression. The default accepts tags such as // REQ: HWR-123. Set the pattern
to the tag format of your project.

**Violation**

.. code-block:: systemverilog

   // Output register
   always_ff @(posedge clk_i) begin

**Fix**

.. code-block:: systemverilog

   // Output register
   // REQ: HWR-123
   always_ff @(posedge clk_i) begin
