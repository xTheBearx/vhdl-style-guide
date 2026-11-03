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

|unfixable|

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

|unfixable|

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
