.. include:: includes.rst

SystemVerilog Literal Rules
---------------------------

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
