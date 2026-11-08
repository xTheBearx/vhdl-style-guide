.. include:: includes.rst

Verilog and SystemVerilog Always Rules
--------------------------------------

sv_always_001
#############

|phase_1| |error| |structure|

Alias: :code:`sv_always_comb`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

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

This rule checks that always_comb blocks use blocking assignments (=), not nonblocking ones (<=). In a Verilog
file, which has no always_comb, it checks the always blocks of combinational logic: always @*, and those whose
event control has no edge.

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

sv_always_021
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_asynchronous_resets`

This rule checks for registers reset synchronously, an edge triggered always block with one clock whose first if
tests a reset, as the STARC guide recommends (1.3.1.2): reset them asynchronously. Resets are told by the words
of their names, as for port_028. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i)
       if (!rst_ni) q <= 1'b0;
       else q <= d;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) q <= 1'b0;
       else q <= d;

sv_always_022
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_clock_as_data`

This rule checks that clocks, the signals of the edge events of always blocks other than their asynchronous
resets, are not read as data, in assignments or conditions, as the STARC guide asks (1.4.3.4, 3.3.3.1): a clock
drives only the clock inputs of registers. Signals named as resets, as for port_028, are not taken for clocks. It
is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) q <= d;
   assign y = clk_i & en;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) q <= d;
   assign y = en;

sv_always_023
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_reset_logic`

This rule checks that the asynchronous resets of the always blocks of a module are not made by logic in the
module, a continuous assignment of an expression or an assignment in a combinational always block, as the STARC
guide recommends (1.3.2.1): generate resets in a module of their own. It is disabled by default; the starc rule
set enables it.

**Violation**

.. code-block:: systemverilog

   assign rst_n = rst_a_n & rst_b_n;
   always_ff @(posedge clk_i or negedge rst_n) ...

**Fix**

Generate the reset in a reset module and bring it in through a port.

sv_always_024
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_calls_in_reset`

This rule checks for function calls in the reset test and reset branch of an always block with an asynchronous
reset, as the STARC guide asks (2.1.2.1). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (!rst_ni) q <= init(1'b0);

**Fix**

.. code-block:: systemverilog

   if (!rst_ni) q <= 1'b0;

sv_always_025
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_no_latch_reset`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks for latches with an asynchronous reset or set, an always_latch block whose first if tests a
reset, as the STARC guide asks (2.4.1.3). Resets are told by the words of their names, as for port_028. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_latch
       if (!rst_ni) q <= 1'b0;
       else if (en) q <= d;

**Fix**

.. code-block:: systemverilog

   always_latch
       if (en) q <= d;

sv_always_026
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_unit_delay`

This rule checks that the nonblocking assignments of edge triggered always blocks have a unit delay, such as q <=
#1 d, as the STARC guide recommends (2.3.1.3) so that simulation shows the register change after the clock edge.
It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) q <= d;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) q <= #1 d;

sv_always_027
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_register_reset`

This rule checks that every register has a reset: an edge triggered always block without an asynchronous reset
holds registers without reset, but for those assigned in the reset branch of an if at the top level of the block
that tests a synchronous reset. Resets are told by the words of their names, as for port_028. Registers written through an index that is a name, such as mem[addr], are
memories and are not checked; the registers of an always block with a reset are checked by sv_always_016.
Registers without a reset on purpose, such as the flip-flops of a synchronizer, should be justified. It is disabled
by default; the do254 rule set enables it (SS14).

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i)
       q <= d;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) q <= 1'b0;
       else q <= d;

sv_always_028
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_consistent_reset`

This rule checks that a reset is used with one polarity and one style throughout a file: active low or active
high, and asynchronous or synchronous. The asynchronous resets of an edge triggered always block are the events of
its event control that its first if tests, active low on negedge; its synchronous reset is a signal with a reset
name, as for port_028, that the first if of a block with one clock tests. A reset that is active low in one block
and active high in another, or both asynchronous and synchronous, behaves unexpectedly around reset. It is
disabled by default; the do254 rule set enables it (SS13).

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) a <= 1'b0;
       else a <= d;

   always_ff @(posedge clk_i)
       if (rst_ni) b <= 1'b0;
       else b <= d;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) b <= 1'b0;
       else b <= d;

sv_always_029
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_label`

This rule checks that always blocks are labelled: their statement is a begin-end block with a name, such as
begin : p_count, so that reports, waveforms and reviews can name the block. It is disabled by default; the do254
rule set enables it (DR1), with sv_generate_001 for the blocks of generate constructs.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count <= count + 1;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin : p_count
       count <= count + 1;
   end

sv_always_030
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_read_before_assignment`

This rule checks that a combinational always block assigns each variable on every path before it reads it. It is
disabled by default; the do254 rule set enables it (CP10, SS3).

A variable read before it is assigned holds the value of the last run of the block: synthesis makes a latch, or a
combinational loop when the variable is a signal of the module, and simulation and hardware can differ. The rule
follows the paths through if and case statements: an if without else, or a case without a default item that is
not a unique or priority case, may assign nothing. Variables assigned through an element, a slice or a member
are not checked.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       if (enable) sum = a + b;
       result = sum;
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       sum = '0;
       if (enable) sum = a + b;
       result = sum;
   end

sv_always_031
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_variable_holds_state`

This rule checks that an edge triggered always block assigns each variable it writes with blocking assignments
on every path before it reads it. It is disabled by default; the do254 rule set enables it (CP10), and the
do254_plus rule set (VAR).

Such a variable keeps its value from the previous clock edge, so synthesis makes it a register. That register is
easy to overlook, because no nonblocking assignment shows it. Assign the variable before reading it, or make the
register explicit with a nonblocking assignment.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count = count + 1;
       count_o <= count;
   end

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin
       count_q <= count_q + 1;
   end

sv_always_032
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_always_default_assignment`

This rule checks that a combinational always block gives every signal it assigns in if, case and loop statements
a default value at its start. It is disabled by default; the do254_plus rule set enables it (DEFAULT).

A default assignment before the if and case statements makes sure every path assigns the signal, so no latch can be
inferred, and shows the value of the signal when no branch changes it. Variables declared in the block, and loop
variables, are not checked.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       case (state_q)
           Idle:    state_d = Start;
           default: state_d = Idle;
       endcase
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       state_d = state_q;
       case (state_q)
           Idle:    state_d = Start;
           default: state_d = Idle;
       endcase
   end
