.. include:: includes.rst

Verilog and SystemVerilog Literal Rules
---------------------------------------

sv_literal_001
##############

|phase_1| |error| |structure|

Alias: :code:`sv_literal_undersized_binary`

This rule checks that a sized binary literal has a digit for each bit, as Verible's
undersized-binary-literal rule does; the fix adds leading zeros. Zero, as in 4'b0, is allowed.

**Violation**

.. code-block:: systemverilog

   assign mode = 4'b1;

**Fix**

.. code-block:: systemverilog

   assign mode = 4'b0001;

sv_literal_002
##############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_literal_truncated_numeric`

This rule checks that the value of a sized literal fits its width, as Verible's truncated-numeric-literal
rule does.

**Violation**

.. code-block:: systemverilog

   assign mask = 4'hFF;

**Fix**

.. code-block:: systemverilog

   assign mask = 8'hFF;

sv_literal_003
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_parameter_base`

This rule checks that parameter values are written with an explicit base, such as 'd8, as the STARC guide
asks (1.1.4.8). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   parameter int Depth = 8;

**Fix**

.. code-block:: systemverilog

   parameter int Depth = 'd8;

sv_literal_004
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_wide_unsized`

This rule checks that a literal whose value needs more than 32 bits has an explicit width, as the STARC
guide asks (1.1.4.9). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   assign seed = 'h1_0000_0000;

**Fix**

.. code-block:: systemverilog

   assign seed = 33'h1_0000_0000;

sv_literal_005
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_x_z_comparison`

This rule checks for comparisons with x or z, which are never true in synthesis, as the STARC guide asks
(2.10.1.4). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (data == 8'bx) begin

**Fix**

.. code-block:: systemverilog

   if (data_valid) begin

sv_literal_006
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_x_or_z`

This rule checks for literals with x or z digits, as the STARC guide asks (2.10.1.6, and 2.1.6.5 for indexes).
The don't-care of the default item of a case statement (2.8.3.1) and the wildcards of casez and casex items are
allowed; comparisons with x or z are checked by sv_literal_005. It is disabled by default; the starc rule set
enables it.

**Violation**

.. code-block:: systemverilog

   assign y = 8'bxxxx_0000;

**Fix**

.. code-block:: systemverilog

   assign y = 8'b0000_0000;

sv_literal_007
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_sized_conditions`

This rule checks that the constants of the conditions of if statements and conditional operators have a width,
such as 4'd3 rather than 3 or 'd3, as the STARC guide asks (2.10.3.6). Indexes and unbased fill literals such as
'0 are not checked. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (count == 3) done <= 1'b1;

**Fix**

.. code-block:: systemverilog

   if (count == 4'd3) done <= 1'b1;

sv_literal_008
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_explicit_base`

This rule checks that the numbers assigned to signals and compared with them are written with a base, such as 'd5
or 8'h1F rather than 5, as the STARC guide recommends (2.10.3.5). Indexes, dimensions, loop headers, delays,
replication counts and the conditions sv_literal_007 checks are not checked. It is disabled by default; the starc
rule set enables it.

**Violation**

.. code-block:: systemverilog

   count <= 5;

**Fix**

.. code-block:: systemverilog

   count <= 'd5;

sv_literal_009
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_no_negative_values`

This rule checks for negative constants assigned to signals, such as count <= -1, as the STARC guide asks
(2.10.4.5, 2.10.4.6). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   count <= -1;

**Fix**

.. code-block:: systemverilog

   count <= '1;

sv_literal_010
##############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_literal_named_numbers`

This rule checks for numbers other than 0 and 1 in the code, as the STARC guide recommends (3.2.2.1, 4.1.2.1):
name them with parameters. Parameter declarations, dimensions, indexes, delays, replication counts, loop headers
and case items are not checked. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   if (count == 8'd200) done <= 1'b1;

**Fix**

.. code-block:: systemverilog

   localparam logic [7:0] Limit = 8'd200;
   if (count == Limit) done <= 1'b1;
