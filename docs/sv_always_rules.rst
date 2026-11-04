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
