.. include:: includes.rst

SystemVerilog Declaration Rules
-------------------------------

sv_declaration_001
##################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_explicit_parameter_storage_type`

This rule checks that parameters and localparams are declared with a type, such as int or logic [7:0], as
Verible's explicit-parameter-storage-type rule does.

**Violation**

.. code-block:: systemverilog

   parameter Depth = 8;

**Fix**

.. code-block:: systemverilog

   parameter int Depth = 8;

sv_declaration_002
##################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_parameter_default`

This rule checks that every parameter has a default value, as the STARC guide asks (3.1.5.3). It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo #(parameter int Depth) ();

**Fix**

.. code-block:: systemverilog

   module fifo #(parameter int Depth = 4) ();

sv_declaration_003
##################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_one_per_line`

This rule checks that a declaration names one signal, as the STARC guide recommends (3.1.3.4), so each can have
its own comment. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic valid, ready;

**Fix**

.. code-block:: systemverilog

   logic valid;  // the data is valid
   logic ready;  // the sink takes the data
