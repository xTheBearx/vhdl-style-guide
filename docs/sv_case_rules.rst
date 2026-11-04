.. include:: includes.rst

SystemVerilog Case Rules
------------------------

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
