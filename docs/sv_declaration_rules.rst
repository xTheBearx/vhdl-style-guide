.. include:: includes.rst

Verilog and SystemVerilog Declaration Rules
-------------------------------------------

sv_declaration_001
##################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_explicit_parameter_storage_type`

This rule checks that parameters and localparams are declared with a type, such as int or logic [7:0], as
Verible's explicit-parameter-storage-type rule does. In a Verilog file, which can give a parameter only the types
integer, real, realtime and time, a range or signed is taken as its type, as in parameter [7:0] Mask.

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

sv_declaration_004
##################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_no_initial_value`

This rule checks for initial values on signals and output ports: the declaration of a variable of a module, or of
an output or inout port, with an initial value, such as logic q = 1'b0. Synthesis may ignore the value or turn it
into a power-on value of the target, so simulation and hardware can start differently; reset the register instead.
Constants, nets, whose initial value is a continuous assignment, the variables of functions, tasks, classes and
procedural blocks, and the default values of input ports are not reported; initial blocks are reported by
sv_statement_004. It is disabled by default; the do254 rule set enables it (SS16).

**Violation**

.. code-block:: systemverilog

   logic busy = 1'b0;

**Fix**

.. code-block:: systemverilog

   logic busy;

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) busy <= 1'b0;
       else busy <= start_i;
