.. include:: includes.rst

Verilog and SystemVerilog Typedef Rules
---------------------------------------

sv_typedef_001
##############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_typedef_enums`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that enum types are declared with typedef, not anonymously in a declaration, as Verible's
typedef-enums rule does.

**Violation**

.. code-block:: systemverilog

   enum logic {Idle, Busy} state;

**Fix**

.. code-block:: systemverilog

   typedef enum logic {Idle, Busy} state_e;
   state_e state;

sv_typedef_002
##############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_typedef_structs_unions`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that struct and union types are declared with typedef, not anonymously in a declaration, as
Verible's typedef-structs-unions rule does.

**Violation**

.. code-block:: systemverilog

   struct packed {logic a;} beat;

**Fix**

.. code-block:: systemverilog

   typedef struct packed {logic a;} beat_t;
   beat_t beat;
