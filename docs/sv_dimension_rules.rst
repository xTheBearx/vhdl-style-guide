.. include:: includes.rst

SystemVerilog Dimension Rules
-----------------------------

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
unpacked-dimensions-range-ordering rule does.

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
