.. include:: includes.rst

Verilog and SystemVerilog Dimension Rules
-----------------------------------------

sv_dimension_001
################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_dimension_packed_range_ordering`

This rule checks that packed dimensions are written from the most to the least significant bit, such as
[7:0], as Verible's packed-dimensions-range-ordering rule does.

**Violation**

.. code-block:: systemverilog

   logic [0:7] data;

**Fix**

.. code-block:: systemverilog

   logic [7:0] data;

sv_dimension_002
################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_dimension_unpacked_range_ordering`

This rule checks that unpacked dimensions are written as [0:N-1] or [N], as Verible's
unpacked-dimensions-range-ordering rule does. Verilog files, which cannot write [N], are asked for [0:N-1].

**Violation**

.. code-block:: systemverilog

   logic [7:0] mem [15:0];

**Fix**

.. code-block:: systemverilog

   logic [7:0] mem [16];

sv_dimension_003
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_dimension_lsb_zero`

This rule checks that the least significant bit of a packed dimension is 0, as the STARC guide asks (2.1.6.2),
for dimensions whose bounds are numbers. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic [8:1] data;

**Fix**

.. code-block:: systemverilog

   logic [7:0] data;

sv_dimension_004
################

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_dimension_parameterized_ports`

This rule checks that the packed dimensions of ports are written with parameters, not numbers, as the STARC guide
recommends (1.1.4.7, 3.1.5.1, 3.1.5.2), so the module can be reused with other widths. It is disabled by default;
the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo (input logic [7:0] data_i);

**Fix**

.. code-block:: systemverilog

   module fifo #(parameter int Width = 8) (input logic [Width-1:0] data_i);
