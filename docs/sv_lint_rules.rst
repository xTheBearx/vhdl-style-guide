.. include:: includes.rst

SystemVerilog Lint Rules
------------------------

sv_lint_001
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_widths`

This rule checks for widths that do not match, such as an assignment that truncates a value, as slang
reports them (WidthTruncate, WidthExpand, PortWidthTruncate and PortWidthExpand).

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   logic [3:0] y;
   assign y = a_i;  // a_i is 8 bits

**Fix**

.. code-block:: systemverilog

   logic [3:0] y;
   assign y = a_i[3:0];

sv_lint_002
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_latches`

This rule checks for latches: variables that combinational logic does not assign on every path.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       if (sel_i) y = a_i;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       y = '0;
       if (sel_i) y = a_i;
   end

sv_lint_003
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_multiple_drivers`

This rule checks for variables driven by more than one process or continuous assignment.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   assign ready = 1'b0;
   always_ff @(posedge clk_i) ready <= 1'b1;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) ready <= 1'b1;

sv_lint_004
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_implicit_nets`

This rule checks for nets declared implicitly by their use, which hides typing mistakes; the default_nettype
none directive makes them errors. A file that uses modules, packages or macros of other files is not
checked, as a name defined there would look like an implicit net.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   assign valid = data_i[0];  // valid is not declared

**Fix**

.. code-block:: systemverilog

   logic valid;
   assign valid = data_i[0];

sv_lint_005
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_unused`

This rule checks for declarations that are never used: ports, variables, nets, parameters and imports, and
variables assigned but never read. A file that uses modules, packages or macros of other files is not
checked, as a signal read there would look unused.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   logic spare;
   assign spare = a_i;

**Fix**

.. code-block:: systemverilog

   // removed

sv_lint_006
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_case_items`

This rule checks for case items that duplicate or overlap others, which can never be matched.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   case (s_i)
       4'd1: y = 0;
       4'd1: y = 1;

**Fix**

.. code-block:: systemverilog

   case (s_i)
       4'd1: y = 0;
       4'd2: y = 1;

sv_lint_007
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_signedness`

This rule checks for comparisons and conversions between signed and unsigned values.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   if (count == -1) begin  // count is unsigned

**Fix**

.. code-block:: systemverilog

   if (count == '1) begin

sv_lint_008
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_sensitivity_list`

This rule checks that the sensitivity list of a combinational always block names every signal and port of the
file that the block reads. A missing signal makes simulation differ from synthesis; always_comb or always @*
avoids the list altogether.

The signals a function or task of the file reads count as read by the blocks that call it. A hierarchical name,
such as u_sub.valid, must be listed as written; a member of a signal, such as cfg.mode, needs the signal. A
variable the block declares, or writes on every path before reading it, needs no entry: a write in both branches
of an if and else, or in every item of a case with a default, is on every path.

.. NOTE:: This is a lint rule. It runs in lint mode.

**Violation**

.. code-block:: systemverilog

   always @(a_i) begin
       y = a_i & b_i;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       y = a_i & b_i;
   end

sv_lint_009
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_other_warnings`

This rule reports the other warnings slang finds when it elaborates the file, such as an index out of range or
arithmetic between operands of different types, with slang's name of the warning.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   assign last = data[8];  // data is [7:0]

**Fix**

.. code-block:: systemverilog

   assign last = data[7];

sv_lint_010
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_undriven`

This rule checks for variables, nets and output ports that nothing drives. A file that uses modules, packages
or macros of other files is not checked, as a signal driven there would look undriven.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

**Violation**

.. code-block:: systemverilog

   module counter (output logic [7:0] count_o);
   endmodule

**Fix**

.. code-block:: systemverilog

   module counter (output logic [7:0] count_o);
       assign count_o = '0;
   endmodule

sv_lint_011
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_verilator`

This rule reports the warnings of Verilator, when it is installed, for checks slang does not make: blocking
assignments in clocked processes (BLKSEQ), non-blocking assignments in combinational ones (COMBDLY), and others.
The verilator_warnings option lists the warnings reported, by Verilator's names; by default those whose checks
slang does not make, but for MULTIDRIVEN and CASEINCOMPLETE, which sv_lint_012 and sv_lint_013 report.

Verilator lints the SystemVerilog files of a run together; the systemverilog section of the configuration turns
it off with :code:`verilator: false`, or names the program with :code:`verilator: /path/to/verilator`.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
   reports nothing.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk) begin
       count = count + 1;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk) begin
       count <= count + 1;
   end

sv_lint_012
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_verilator_multiple_drivers`

This rule reports signals assigned in always blocks of different clocks (Verilator's MULTIDRIVEN), which
synthesis cannot build as one register. Verilator lints the SystemVerilog files of a run when it is installed, see
sv_lint_011.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
   reports nothing.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_a) busy <= 1'b1;
   always_ff @(posedge clk_b) if (done) busy <= 1'b0;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_a) begin
       if (done_a) busy <= 1'b0;
       else busy <= 1'b1;
   end

sv_lint_013
###########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`sv_lint_verilator_incomplete_case`

This rule reports case statements that do not cover every value of their selector and have no default
branch (Verilator's CASEINCOMPLETE). Verilator lints the SystemVerilog files of a run when it is installed, see
sv_lint_011.

.. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
   reports nothing.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       case (sel)
           2'b00: y = a;
           2'b01: y = b;
       endcase
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       case (sel)
           2'b00: y = a;
           2'b01: y = b;
           default: y = '0;
       endcase
   end
