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
