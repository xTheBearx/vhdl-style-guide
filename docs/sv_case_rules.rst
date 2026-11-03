.. include:: includes.rst

SystemVerilog Case Rules
------------------------

sv_case_001
###########

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_case_missing_default`

This rule checks that a case statement has a default item, unless it is unique or unique0 and
**exempt_unique** is yes, the default.

|unfixable|

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

|unfixable|

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
