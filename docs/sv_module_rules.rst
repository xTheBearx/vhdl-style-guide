.. include:: includes.rst

SystemVerilog Module Rules
--------------------------

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

This rule checks for text macros that define a constant, such as `define WIDTH 8, as the STARC guide asks
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
