.. include:: includes.rst

SystemVerilog Always Rules
--------------------------

sv_always_001
#############

|phase_1| |error| |structure|

Alias: :code:`sv_always_comb`

This rule checks that combinational logic uses always_comb rather than always @* or always @(*).

**Violation**

.. code-block:: systemverilog

   always @(*) begin
       sum = a + b;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       sum = a + b;
   end

sv_always_002
#############

|phase_1| |error| |structure|

Alias: :code:`sv_always_comb_blocking`

This rule checks that always_comb blocks use blocking assignments (=), not nonblocking ones (<=).

**Violation**

.. code-block:: systemverilog

   always_comb begin
       sum <= a + b;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       sum = a + b;
   end

sv_always_003
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_always_ff_non_blocking`

This rule checks that sequential logic, in always_ff blocks and in always blocks clocked on an edge, uses
nonblocking assignments (<=). Blocking assignments in the header of a for loop are allowed; with
**waive_for_locals** set to yes, so are blocking assignments to variables declared in the block.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count_q = count_d;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count_q <= count_d;
   end

sv_always_004
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_always_mixed_assignments`

This rule checks that an always block does not mix blocking (=) and nonblocking (<=) assignments.
Assignments in the header of a for loop are not counted.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count_q <= count_d;
       valid_q = valid_d;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count_q <= count_d;
       valid_q <= valid_d;
   end

sv_always_005
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_single_event_control`

This rule checks that an always block has a single event control, at its start, as the STARC guide asks
(2.2.2.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always @(posedge clk_i) begin
       @(posedge clk_i) q <= d;

**Fix**

.. code-block:: systemverilog

   always @(posedge clk_i) begin
       q <= d;

sv_always_006
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_one_top_level_statement`

This rule checks that an always block holds at most one if or case statement at its top level, as the STARC
guide asks (2.6.2.1). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       if (a) y = 1;
       if (b) z = 1;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       if (a) y = 1;
   end
   always_comb begin
       if (b) z = 1;
   end

sv_always_007
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_falling_edge_clock`

This rule checks for registers clocked on the falling edge of their clock, as the STARC guide recommends
(1.4.3.6). In an always block with several events, those tested by its first if are asynchronous resets, which
may use negedge; the others are clocks. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(negedge clk_i) begin
       q <= d;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       q <= d;
   end

sv_always_008
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_outputs`

This rule checks that an always block assigns at most **maximum_outputs** signals, 15 by default, as the STARC
guide asks (2.6.1.3; it recommends 5). It is disabled by default; the starc rule set enables it.

**Violation**

An always block that assigns 16 signals.

**Fix**

Split it into always blocks of related signals.

sv_always_009
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_length`

This rule checks that an always block is at most **maximum_lines** lines long, 300 by default, as the STARC
guide asks (2.6.1.4). It is disabled by default; the starc rule set enables it.

**Violation**

An always block of 301 lines.

**Fix**

Split it into always blocks of related signals.

sv_always_010
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_constant_in_sensitivity`

This rule checks for constants, such as 1'b1 or a parameter, in the sensitivity list of an always block, as the
STARC guide asks (2.2.2.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always @(a or 1'b1) begin
       y = a;
   end

**Fix**

.. code-block:: systemverilog

   always @(a) begin
       y = a;
   end

sv_always_011
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_output_in_sensitivity`

This rule checks that a combinational always block does not list in its sensitivity list a signal it assigns, as
the STARC guide asks (2.6.2.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always @(a or y) begin
       y = a;
   end

**Fix**

.. code-block:: systemverilog

   always @(a) begin
       y = a;
   end

sv_always_012
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_one_clock`

This rule checks that an edge triggered always block has one clock, on one edge, as the STARC guide asks
(2.3.3.1, 2.3.3.2). The events its first if tests are asynchronous resets, not clocks. It is disabled by default;
the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_a or posedge clk_b) begin
       q <= d;
   end

**Fix**

Split the always block into one for each clock.

sv_always_013
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_reset_active_low`

This rule checks that an asynchronous reset is active low, tested on its falling edge with negedge, as the STARC
guide recommends (2.3.6.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or posedge rst_i) begin
       if (rst_i) q <= 1'b0;
       else q <= d;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni) begin
       if (!rst_ni) q <= 1'b0;
       else q <= d;
   end

sv_always_014
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_one_asynchronous_reset`

This rule checks that a register has at most one asynchronous reset or set, as the STARC guide asks (1.3.1.7,
2.3.1.7): an always block with more than one event besides its clock. It is disabled by default; the starc rule
set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni or negedge set_ni) begin
   end

**Fix**

Keep one asynchronous reset, and set the register synchronously.

sv_always_015
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_reset_edge_polarity`

This rule checks that the edge of an asynchronous reset matches the polarity its if tests: negedge for a reset
tested low, such as if (!rst_ni), and posedge for one tested high, as the STARC guide asks (2.3.1.6). It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or posedge rst_ni)
       if (!rst_ni) q <= 1'b0;
       else q <= d;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) q <= 1'b0;
       else q <= d;

sv_always_016
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_reset_all_registers`

This rule checks that an always block with an asynchronous reset resets every register it assigns, as the STARC
guide recommends (2.3.6.1): put registers without reset in an always block of their own. It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) count <= '0;
       else begin
           count <= count + 1;
           data <= data_i;
       end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) count <= '0;
       else count <= count + 1;

   always_ff @(posedge clk_i) data <= data_i;

sv_always_017
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_assign_once`

This rule checks that a sequential always block assigns a signal once in a sequence of statements, not first a
default and then again in a later statement, as the STARC guide asks (2.2.3.3); in a combinational block it
checks nonblocking assignments the same way (2.2.3.2). The signals are compared by their whole target, so q[0]
and q[1] are different. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       q <= 1'b0;
       if (load) q <= d;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i)
       if (load) q <= d;
       else q <= 1'b0;

sv_always_018
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_one_driver_block`

This rule checks that a signal is assigned in one procedural block only, one always or initial block, as the
STARC guide asks (4.1.4.1, 4.1.4.2). Variables declared inside a block are not checked, nor blocks in different
branches of generate constructs. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   initial reset_n = 1'b0;
   initial #100 reset_n = 1'b1;

**Fix**

.. code-block:: systemverilog

   initial begin
       reset_n = 1'b0;
       #100 reset_n = 1'b1;
   end

sv_always_019
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_constant_registers`

This rule checks for registers that an edge triggered always block only ever assigns one constant, so their data
input is constant, as the STARC guide recommends (2.3.5.1, 3.3.3.2). A part of a signal, such as q[0], is not
reported if the block also assigns other values to the signal, nor are the registers of blocks that call tasks,
which may assign them too. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) ready <= 1'b1;
       else ready <= 1'b1;

**Fix**

.. code-block:: systemverilog

   assign ready = 1'b1;

sv_always_020
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_reset_loops`

This rule checks that a for loop of an always block with an asynchronous reset does not hold the reset test, an
if on one of the signals of its event control, as the STARC guide recommends (2.9.2.4): use one loop in the reset
branch and another in the other branch. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   for (int i = 0; i < 4; i++)
       if (!rst_ni) q[i] <= 1'b0;
       else q[i] <= d[i];

**Fix**

.. code-block:: systemverilog

   if (!rst_ni) for (int i = 0; i < 4; i++) q[i] <= 1'b0;
   else for (int i = 0; i < 4; i++) q[i] <= d[i];
