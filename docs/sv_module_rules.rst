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
