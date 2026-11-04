.. include:: includes.rst

SystemVerilog Statement Rules
-----------------------------

sv_statement_001
################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_statement_explicit_begin`

This rule checks that the statement of an if, else, for, foreach, while, repeat, forever, always or initial
is a begin-end block, as Verible's explicit-begin rule does. An else if needs no block of its own.

**Violation**

.. code-block:: systemverilog

   if (valid_i)
       data_d = data_i;

**Fix**

.. code-block:: systemverilog

   if (valid_i) begin
       data_d = data_i;
   end

sv_statement_002
################

|phase_1| |error| |structure|

Alias: :code:`sv_statement_consecutive_null_statements`

This rule checks for consecutive null statements, such as ;;.

**Violation**

.. code-block:: systemverilog

   count_d = count_q + 1;;

**Fix**

.. code-block:: systemverilog

   count_d = count_q + 1;

sv_statement_003
################

|phase_1| |disabled| |error| |structure|

Alias: :code:`sv_statement_one_per_line`

This rule checks for more than one statement or declaration on a line, as the STARC guide asks
(3.1.4.4, at most one assignment per line). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   valid_d = 1'b0; ready_d = 1'b1;

**Fix**

.. code-block:: systemverilog

   valid_d = 1'b0;
   ready_d = 1'b1;

sv_statement_004
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_no_initial`

This rule checks for initial blocks in design code, which synthesis ignores, as the STARC guide asks
(2.3.4.1, 2.3.4.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   initial count_q = '0;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni) begin
       if (!rst_ni) count_q <= '0;

sv_statement_005
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_no_fork`

This rule checks for fork-join blocks in design code, as the STARC guide asks (2.7.4.3). It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   fork
       a = 1;
   join

**Fix**

.. code-block:: systemverilog

   begin
       a = 1;
   end

sv_statement_006
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_empty_branch`

This rule checks for empty branches of if and case statements, such as a case item with only a semicolon, as
the STARC guide asks (2.7.2.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   Idle: ;

**Fix**

.. code-block:: systemverilog

   Idle: state_d = Busy;

sv_statement_007
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_nested_conditional_operator`

This rule checks for conditional operators nested in the branches of another, as the STARC guide asks (2.1.5.1):
one level only. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign y = a ? b : c ? d : e;

**Fix**

.. code-block:: systemverilog

   always_comb begin
       if (a) begin
           y = b;
       end else if (c) begin
           y = d;
       end else begin
           y = e;
       end
   end

sv_statement_008
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_if_depth`

This rule checks that if statements are nested at most **maximum_depth** deep, 7 by default, as the STARC guide
asks (2.7.3.1). An else if continues its if, so it does not nest deeper. It is disabled by default; the starc rule
set enables it.

**Violation**

Eight if statements, each inside the branch of the one before.

**Fix**

Combine the conditions, or move the inner logic to a function or an always block of its own.

sv_statement_009
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_loop_variable`

This rule checks that the body of a for loop does not change its loop variable, as the STARC guide asks
(2.9.1.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   for (int i = 0; i < 8; i++) begin
       i = i + 1;
   end

**Fix**

.. code-block:: systemverilog

   for (int i = 0; i < 8; i += 2) begin
   end

sv_statement_010
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_if_chain_else`

This rule checks that a chain of if and else if in combinational logic ends with an else, as the STARC guide asks
(2.7.1.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_comb begin
       if (a) begin
           y = 1'b0;
       end else if (b) begin
           y = 1'b1;
       end
   end

**Fix**

.. code-block:: systemverilog

   always_comb begin
       if (a) begin
           y = 1'b0;
       end else begin
           y = 1'b1;
       end
   end

sv_statement_011
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_no_arithmetic_in_if`

This rule checks for arithmetic in the condition of an if statement, as the STARC guide asks (2.10.7.1): compute
it in a signal of its own. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (count + 1 == limit) begin
       done = 1'b1;
   end

**Fix**

.. code-block:: systemverilog

   assign next_count = count + 1;
   ...
   if (next_count == limit) begin
       done = 1'b1;
   end

sv_statement_012
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_parenthesize_logical`

This rule checks that && and || are not mixed without parentheses, as the STARC guide asks (2.10.1.2). It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign y = a && b || c;

**Fix**

.. code-block:: systemverilog

   assign y = (a && b) || c;

sv_statement_013
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_divide_signals`

This rule checks that the operands of / and % are plain signals or constants, not expressions, as the STARC guide
asks (2.10.8.1). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign y = (a + b) / c;

**Fix**

.. code-block:: systemverilog

   assign sum = a + b;
   assign y = sum / c;

sv_statement_014
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_fork_join_length`

This rule checks that a fork join block is at most **maximum_lines** lines long, 5 by default, as the STARC guide
recommends (4.1.2.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   fork
       send(a);
       send(b);
       send(c);
       receive(d);
   join

**Fix**

.. code-block:: systemverilog

   fork
       send_all();
       receive(d);
   join

sv_statement_015
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_integer_delays`

This rule checks that delays are non-negative integers, not real or negative numbers, as the STARC guide asks
(2.3.1.5). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   #(1.5) q = d;

**Fix**

.. code-block:: systemverilog

   #2 q = d;

sv_statement_016
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_delays_in_always`

This rule checks for delays in continuous assignments and net declarations, as the STARC guide recommends
(2.3.1.4): give delays only in always blocks. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign #1 y = a;

**Fix**

.. code-block:: systemverilog

   assign y = a;

sv_statement_017
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_tristate_enable`

This rule checks that the enable of a tri-state buffer, the condition of a conditional operator with a z value,
is a plain signal, not an expression, as the STARC guide recommends (2.5.1.2). It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign bus = (oe & sel) ? data : 'z;

**Fix**

.. code-block:: systemverilog

   assign enable = oe & sel;
   assign bus = enable ? data : 'z;

sv_statement_018
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_tristate_conditions`

This rule checks that tri-state signals, the signals the file assigns a value with z digits, are not tested in if
conditions or used as case selectors, as the STARC guide asks (2.5.1.7, 2.5.1.8, 2.5.1.9). A case statement whose
default assigns x may use them. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign bus = oe ? data : 'z;
   always_comb if (bus) y = 1'b1; else y = 1'b0;

**Fix**

Test the signal that drives the bus, data, instead.

sv_statement_019
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_same_branches`

This rule checks for branches of an if, else if chain with the same statements, as the STARC guide recommends
(2.7.2.1): merge their conditions. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (a) y = 1'b1;
   else if (b) y = 1'b1;
   else y = 1'b0;

**Fix**

.. code-block:: systemverilog

   if (a || b) y = 1'b1;
   else y = 1'b0;

sv_statement_020
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_repeated_conditions`

This rule checks for conditions of an if, else if chain that repeat an earlier condition of the chain, so their
branch is never taken, as the STARC guide asks (2.7.2.2). It is disabled by default; the starc rule set enables
it.

**Violation**

.. code-block:: systemverilog

   if (a) y = 1'b1;
   else if (a) y = 1'b0;

**Fix**

.. code-block:: systemverilog

   if (a) y = 1'b1;

sv_statement_021
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_arithmetic_parentheses`

This rule checks that an expression with two or more arithmetic operators, such as a + b - c, has parentheses
showing their order, as the STARC guide recommends (2.10.1.3). It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   assign sum = a + b - c;

**Fix**

.. code-block:: systemverilog

   assign sum = (a + b) - c;

sv_statement_022
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_conditional_arithmetic`

This rule checks for arithmetic in the values of a conditional operator in an assignment, such as sel ? a + b : c
+ d, as the STARC guide recommends (2.10.5.5): select the operands first, so one adder serves both. Arithmetic in
indexes is not checked. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign y = sel ? a + b : c + d;

**Fix**

.. code-block:: systemverilog

   assign x1 = sel ? a : c;
   assign x2 = sel ? b : d;
   assign y = x1 + x2;

sv_statement_023
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_plain_indexes`

This rule checks that an index that reads a signal is the signal alone, such as mem[addr], not an expression such
as mem[addr + 1], as the STARC guide recommends (2.1.6.3). Indexes with only constants, parameters and loop
variables are not checked. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign y = mem[addr + 1];

**Fix**

.. code-block:: systemverilog

   assign next_addr = addr + 1;
   assign y = mem[next_addr];

sv_statement_024
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_blocking_stimulus`

This rule checks for nonblocking assignments in initial blocks, as the STARC guide recommends (4.1.2.2): drive
test stimulus with blocking assignments. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   initial start <= 1'b1;

**Fix**

.. code-block:: systemverilog

   initial start = 1'b1;

sv_statement_025
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_fstrobe`

This rule checks for $fdisplay, as the STARC guide recommends (4.1.11.1): write result files with $fstrobe, which
writes the values at the end of the time step. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   $fdisplay(log, "%h", data);

**Fix**

.. code-block:: systemverilog

   $fstrobe(log, "%h", data);

sv_statement_026
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_bitwise_operators`

This rule checks for the logical operators &&, || and !, as the STARC guide recommends (2.1.4.2): use the bitwise
operators &, | and ~, also on single bits. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (valid && !stall) q <= d;

**Fix**

.. code-block:: systemverilog

   if (valid & ~stall) q <= d;

sv_statement_027
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_merge_ifs`

This rule checks for an if without else whose only statement is another if without else, as the STARC guide
recommends (2.7.3.4): merge their conditions. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (valid)
       if (ready) q <= d;

**Fix**

.. code-block:: systemverilog

   if (valid & ready) q <= d;

sv_statement_028
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_dont_care_conditions`

This rule checks that don't care signals, the signals the file assigns a value with x digits, are not tested in
if conditions or used as case selectors, as the STARC guide asks (2.8.3.4, 2.8.3.6, 2.8.3.7). A case statement
whose default assigns x may use them. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   default: sel = 2'bxx;
   ...
   if (sel == 2'b01) y = a;

**Fix**

Assign sel a value in every branch, or do not test it.

sv_statement_029
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_loop_computation`

This rule checks for arithmetic, comparisons and logic on signals inside for loops, as the STARC guide recommends
(2.9.2.1, 2.9.2.2): in a loop, compute only with the loop variable and constants. Indexes are not checked. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   for (int i = 0; i < 4; i++) y[i] = a[i] + b;

**Fix**

Compute with signals outside the loop, and use only the loop variable and constants in it.

sv_statement_030
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_delay_parameters`

This rule checks for delays computed with arithmetic in always blocks, such as #(Period / 2), as the STARC guide
recommends (4.1.6.1): compute clock periods once, as parameters. It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   always #(Period / 2) clk = ~clk;

**Fix**

.. code-block:: systemverilog

   localparam int HalfPeriod = Period / 2;
   always #HalfPeriod clk = ~clk;

sv_statement_031
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_one_clock_per_block`

This rule checks that a procedural block toggles at most one signal, with an assignment such as clk = ~clk, as
the STARC guide recommends (4.1.7.1): generate each clock in a block of its own. It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always begin
       #5 clk_a = ~clk_a;
       #5 clk_b = ~clk_b;
   end

**Fix**

.. code-block:: systemverilog

   always #5 clk_a = ~clk_a;
   always #7 clk_b = ~clk_b;

sv_statement_032
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_level_waits`

This rule checks for edge events on signals other than clocks in initial blocks and tasks, such as @(posedge
done), as the STARC guide recommends (4.1.8.4): wait for levels with wait or test them on a clock edge. Clocks
are told by the words of their names, as for port_028. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   initial @(posedge done) $finish;

**Fix**

.. code-block:: systemverilog

   initial begin
       wait (done);
       $finish;
   end

sv_statement_033
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_translate_off`

This rule checks that system tasks for simulation, such as $display or $finish, in modules with ports are between
translate_off and translate_on pragma comments, as the STARC guide asks (4.3.11.3). It is disabled by default;
the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) if (err) $display("error");

**Fix**

.. code-block:: systemverilog

   // synopsys translate_off
   always_ff @(posedge clk_i) if (err) $display("error");
   // synopsys translate_on

sv_statement_034
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_statement_testbench_delays`

This rule checks for delays given as numbers in testbenches, modules without ports, as the STARC guide recommends
(4.1.1.2): give testbench timing with parameters. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   initial #100 rst_n = 1'b1;

**Fix**

.. code-block:: systemverilog

   localparam int ResetTime = 100;
   initial #ResetTime rst_n = 1'b1;
