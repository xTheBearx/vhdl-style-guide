.. include:: includes.rst

Verilog and SystemVerilog Case Rules
------------------------------------

sv_case_001
###########

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_case_missing_default`

This rule checks that a case statement has a default item, unless it is unique or unique0 and
**exempt_unique** is yes, the default.

**Violation**

.. code-block:: systemverilog

   case (state_q)
       Idle: state_d = Busy;
       Busy: state_d = Idle;
   endcase

**Fix**

.. code-block:: systemverilog

   case (state_q)
       Idle:    state_d = Busy;
       Busy:    state_d = Idle;
       default: state_d = Idle;
   endcase

sv_case_002
###########

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_case_default_last`

This rule checks that the default item of a case statement is its last item.

**Violation**

.. code-block:: systemverilog

   case (state_q)
       default: state_d = Idle;
       Idle:    state_d = Busy;
   endcase

**Fix**

.. code-block:: systemverilog

   case (state_q)
       Idle:    state_d = Busy;
       default: state_d = Idle;
   endcase

sv_case_003
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_constant_selector`

This rule checks for case statements whose selector is a constant, such as case (1'b1), as the STARC guide
asks (2.8.5.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (1'b1)
       a: y = 0;

**Fix**

.. code-block:: systemverilog

   if (a) begin
       y = 0;

sv_case_004
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_items`

This rule checks that a case statement has at most **maximum_items** items, 200 by default, as the STARC guide
asks (2.8.2.2). It is disabled by default; the starc rule set enables it.

**Violation**

A case statement of 201 items.

**Fix**

Split the case statement, or use a memory or a function.

sv_case_005
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_no_casex_casez`

This rule checks for casex and casez statements, as the STARC guide recommends (2.8.4.3). It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   casez (sel)
       2'b1?: y = a;
       default: y = b;
   endcase

**Fix**

.. code-block:: systemverilog

   case (sel[1])
       1'b1: y = a;
       default: y = b;
   endcase

sv_case_006
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_constant_labels`

This rule checks that the labels of case items are constants, not signals, as the STARC guide asks (2.8.5.3). It
is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (sel)
       other: y = a;
       default: y = b;
   endcase

**Fix**

.. code-block:: systemverilog

   case (sel)
       2'd1: y = a;
       default: y = b;
   endcase

sv_case_007
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_simple_selector`

This rule checks that the selector of a case statement is a signal, a select or a concatenation, not logic or
arithmetic, as the STARC guide recommends (2.8.5.4). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (a & b)
       1'b1: y = c;
       default: y = d;
   endcase

**Fix**

.. code-block:: systemverilog

   assign both = a & b;
   ...
   case (both)
       1'b1: y = c;
       default: y = d;
   endcase

sv_case_008
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_state_encodings`

This rule checks that the items of a case statement on a state, a selector matching **state_pattern**, a regular
expression matched ignoring case, by default names holding state, are named encodings, parameters or enum values,
not numbers, as the STARC guide asks (2.11.1.3, 2.11.4.2). It is disabled by default; the starc rule set enables
it.

**Violation**

.. code-block:: systemverilog

   case (state)
       2'b00: next_state = 2'b01;

**Fix**

.. code-block:: systemverilog

   case (state)
       Idle: next_state = Busy;

sv_case_009
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_state_count`

This rule checks that a state machine, a case statement whose selector matches **state_pattern**, has at most
**maximum_states** items, 60 by default, as the STARC guide asks (2.11.1.4, 2.11.1.5): split larger ones. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (state)  // 75 states

**Fix**

Split the state machine into two that hand over to each other.

sv_case_010
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_one_state_machine`

This rule checks that a module has at most one state machine, a case statement whose selector matches
**state_pattern**, as the STARC guide recommends (2.11.2.1): put each state machine in a module of its own. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (tx_state) ...
   case (rx_state) ...

**Fix**

Put each state machine in a module of its own.

sv_case_011
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_table_size`

This rule checks the size of the table a case statement makes: at most **maximum_table_inputs** selector bits, 20
by default, **maximum_table_outputs** bits assigned, 12 by default, and **maximum_table_bits** of both, 32 by
default, as the STARC guide recommends (2.8.2.1). The widths come from slang's elaboration of the file. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   case (opcode)  // 24 bits, assigning 16 bits

**Fix**

Split the table into smaller case statements.

sv_case_012
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_case_grouped_wildcards`

This rule checks that the wildcard bits, x, z or ?, of the items of a casex or casez statement are next to each
other, not scattered between other bits, as the STARC guide recommends (2.8.4.4). It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   casez (sel)
       4'b1?0?: y = a;

**Fix**

.. code-block:: systemverilog

   casez (sel)
       4'b10??: y = a;
