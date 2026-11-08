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

sv_module_018
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_names_across_hierarchy`

This rule checks that a signal connected to a port of an instance has the name of the port, apart from prefixes
and suffixes, so a signal keeps its name through the hierarchy. It is disabled by default; the do254 rule set
enables it (DR9).

A signal renamed at each level of the hierarchy is hard to follow from the top to the bottom of the design. The
**strip_prefixes** and **strip_suffixes** options list the parts that are ignored, such as i\_ and _o, which mark
direction or kind; one prefix and one suffix, the longest that fits, are removed and the names compared ignoring
case, as lint_040 does for VHDL, with the same defaults. The default suffixes include those of port names written
by direction, the names sv_naming_016 asks for: _i, _o and _io, with _n or n before them for active low ports, so
tick_o matches tick and tick_i, and rst_n_i or rst_ni matches rst_n. Only named connections of a signal by name
are checked, not selects, expressions, .name or .* connections.

The ports of a module instantiated more than once are not checked: each instance connects its own signals, which
cannot all have the names of the ports. In lint mode the instances of all the files of the run are counted,
otherwise those of the file; an instance array or an instance in a loop generate counts as more than one. lint_040
does the same for VHDL.

**Violation**

.. code-block:: systemverilog

   fifo u_fifo (
       .wr_data_i (payload)
   );

**Fix**

.. code-block:: systemverilog

   fifo u_fifo (
       .wr_data_i (wr_data)
   );

sv_module_019
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_parameter_assertion`

This rule checks that a module with parameters checks their values with an assertion. It is disabled by default;
the do254_plus rule set enables it (GENERIC).

A parameter value outside the range a design supports, such as a width of zero, otherwise goes unnoticed until
the hardware fails. The rule accepts any assertion in the file, an $error, $fatal or $finish, such as one in a
generate if that tests the parameters, or a macro named like an assertion, such as the ASSERT macros of lowRISC; also in code an
ifdef directive leaves out, such as one testing FORMAL. Local parameters are not checked.

**Violation**

.. code-block:: systemverilog

   module fifo #(
       parameter int Depth = 16
   ) (

**Fix**

.. code-block:: systemverilog

   if (Depth & (Depth - 1)) begin : g_depth_check
       $error("Depth must be a power of two");
   end

sv_module_020
#############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_module_inout_port`

This rule checks for inout ports. It is disabled by default; the do254_plus rule set enables it (PORT).

An inout port implies a tri-state driver and belongs only on the top level, for device pins, so the inout ports
of the top level are not reported. The top level is the module the design section of the configuration names
with top; without one, in lint mode with more than one file in the run or with index files given (--index_files
or index_file_list), a module that no file of the run or of the index files instantiates. A file checked on
its own without index files, a run outside lint mode and a file read from standard input do not show the design:
without the design section, every inout port is reported.

A testbench in the run instantiates the top level; name the top in the design section, so its pins are not
reported.

**Violation**

.. code-block:: systemverilog

   module bus_ctrl (
       inout wire [7:0] data_io
   );

**Fix**

.. code-block:: systemverilog

   module bus_ctrl (
       input  logic [7:0] data_i,
       output logic [7:0] data_o,
       output logic       data_oe_o
   );
