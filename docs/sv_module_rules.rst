.. include:: includes.rst

Verilog and SystemVerilog Module Rules
--------------------------------------

sv_module_001
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_module_begin_block`

This rule checks for begin-end blocks directly in a module, outside of any generate construct.

**Violation**

.. code-block:: systemverilog

   module counter;
       begin : gen_count
           assign count = 1'b0;
       end
   endmodule

**Fix**

.. code-block:: systemverilog

   module counter;
       assign count = 1'b0;
   endmodule

sv_module_002
#############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_module_defparam`

This rule checks for defparam statements; set parameters in the instantiation instead.

**Violation**

.. code-block:: systemverilog

   fifo u_fifo (.clk_i);
   defparam u_fifo.Depth = 8;

**Fix**

.. code-block:: systemverilog

   fifo #(.Depth(8)) u_fifo (.clk_i);

sv_module_003
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_ports_by_name`

This rule checks that the ports of an instance are connected by name, never by position, as the STARC guide asks
(3.2.3.1). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   fifo fifo (clk_i, data_i, data_o);

**Fix**

.. code-block:: systemverilog

   fifo fifo (.clk_i(clk_i), .data_i(data_i), .data_o(data_o));

sv_module_004
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_no_constant_output`

This rule checks that output ports are not driven by a constant in a continuous assignment, as the STARC guide
asks (1.1.4.6). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign ready_o = 1'b1;

**Fix**

Drive the output from a register or logic, or remove the port.

sv_module_005
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_no_gate_primitives`

This rule checks for gate primitives, such as and or nand instances, which can build latches and flip-flops out
of gates, as the STARC guide asks (1.2.1.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   nand g_set (q, set_n, qb);

**Fix**

.. code-block:: systemverilog

   assign q = ~(set_n & qb);

sv_module_006
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_no_constant_macros`

This rule checks for text macros that define a constant, such as a define of WIDTH as 8, as the STARC guide asks
(3.2.2.7): use a parameter. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   `define WIDTH 8

**Fix**

.. code-block:: systemverilog

   localparam int Width = 8;

sv_module_007
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_port_order`

This rule checks the order of the ports of a module: clocks, resets, other inputs, outputs, then inout ports, as
the STARC guide recommends (3.1.3.2). Clocks and resets are told by the words of their names, as for port_028:
**clock_words**, **reset_words** and **qualifier_words**. It is disabled by default; the starc rule set enables
it.

**Violation**

.. code-block:: systemverilog

   module fifo (input logic data_i, input logic clk_i, output logic full_o, input logic rst_ni);

**Fix**

.. code-block:: systemverilog

   module fifo (input logic clk_i, input logic rst_ni, input logic data_i, output logic full_o);

sv_module_008
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_no_nested_macros`

This rule checks for text macros used in the definition of other text macros, as the STARC guide recommends
(3.2.2.5). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   `define DEPTH (`WIDTH * 2)

**Fix**

.. code-block:: systemverilog

   localparam int Depth = Width * 2;

sv_module_009
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_port_count`

This rule checks that a module has at most **maximum_ports** ports, 500 by default, as the STARC guide recommends
(1.6.4.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module core (/* 640 ports */);

**Fix**

Split the module into blocks with fewer ports.

sv_module_010
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_latch_modules`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that a module with latches, always_latch blocks, holds no other logic, as the STARC guide
recommends (2.4.1.1, 2.4.1.2): put latches in modules of their own. It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   always_latch if (en) q <= d;
   assign y = q & a;

**Fix**

Move the latch to a module that holds only latches.

sv_module_011
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_tristate_modules`

This rule checks that a module with tri-state buffers, assignments of values with z digits, holds no other logic,
as the STARC guide recommends (2.5.1.1): put tri-state buffers in modules of their own. It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign bus = oe ? data : 'z;
   always_ff @(posedge clk_i) data <= d;

**Fix**

Move the tri-state buffer to a module that holds only tri-state buffers.

sv_module_012
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_no_vendor_primitives`

This rule checks for instances of vendor primitives, the types of the black box libraries that come with mhsg,
such as BUFG or RAMB36E1, as the STARC guide recommends (3.1.2.2): keep technology dependent code apart. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   BUFG u_bufg (.I(clk_in), .O(clk));

**Fix**

Instantiate the primitive in a technology dependent module, or let synthesis infer it.

sv_module_013
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_local_macros`

This rule checks that a text macro defined inside a module is undefined with an undef directive before the end
of the module, so it is used only there, as the STARC guide recommends (1.1.4.4). It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo;
       `define DEPTH 4
   endmodule

**Fix**

.. code-block:: systemverilog

   module fifo;
       `define DEPTH 4
       `undef DEPTH
   endmodule

sv_module_014
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_synchronous_reset_modules`

This rule checks that registers with a synchronous reset are in modules of their own, without other registers, as
the STARC guide recommends (1.3.1.4). Synchronous resets are told as for sv_always_021. It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) if (!srst_n) a <= '0; else a <= d;
   always_ff @(posedge clk_i or negedge rst_n) ...

**Fix**

Move the registers with a synchronous reset to a module of their own.

sv_module_015
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_hierarchy_only`

This rule checks that a module that instantiates other modules holds no logic of its own, always blocks or
continuous assignments, as the STARC guide recommends (1.6.4.1) for the levels of the hierarchy above the basic
blocks. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   sub u_sub (.a(a), .y(y));
   assign z = y & en;

**Fix**

Move the logic into a module of its own and instantiate it.

sv_module_016
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_connection_order`

This rule checks that the named port connections of an instance of a module the file defines are in the order of
the ports of the module, as the STARC guide recommends (3.1.3.1). It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   sub u_sub (.y(y), .a(a));  // sub declares a, then y

**Fix**

.. code-block:: systemverilog

   sub u_sub (.a(a), .y(y));

sv_module_017
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_registered_outputs`

This rule checks that the outputs of a module are registered, not driven by logic of a continuous assignment or a
combinational always block, as the STARC guide recommends (1.6.2.1) for basic blocks. An output assigned a signal
as it is, such as assign y_o = q, is taken to be registered. It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   assign y_o = a & b;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) y_o <= a & b;
