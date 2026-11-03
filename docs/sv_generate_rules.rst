.. include:: includes.rst

SystemVerilog Generate Rules
----------------------------

sv_generate_001
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_generate_label`

This rule checks that the begin-end blocks of generate loops, ifs and cases are labelled.

|unfixable|

**Violation**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin
       assign stage[i] = data_i;
   end

**Fix**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin : gen_stage
       assign stage[i] = data_i;
   end

sv_generate_002
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_generate_label_prefix`

This rule checks that the labels of generate blocks match **pattern**, a regular expression, by default
(g_|gen_).*, as Verible's generate-label-prefix rule does.

|unfixable|

**Violation**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin : stage

**Fix**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin : gen_stage

sv_generate_003
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_generate_v2001_begin`

This rule checks for begin-end blocks directly in a generate region, a Verilog-2001 form.

|unfixable|

**Violation**

.. code-block:: systemverilog

   generate
       begin : gen_logic
           assign valid = 1'b1;
       end
   endgenerate

**Fix**

.. code-block:: systemverilog

   assign valid = 1'b1;

sv_generate_004
###############

|phase_1| |error| |structure|

Alias: :code:`sv_generate_legacy_region`

This rule checks for generate regions: the generate and endgenerate keywords are not needed.

**Violation**

.. code-block:: systemverilog

   generate
       for (genvar i = 0; i < Depth; i++) begin : gen_stage
           assign stage[i] = data_i;
       end
   endgenerate

**Fix**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin : gen_stage
       assign stage[i] = data_i;
   end

sv_generate_005
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_generate_legacy_genvar`

This rule checks for genvar declarations outside of a for loop; declare the genvar in the loop instead.

|unfixable|

**Violation**

.. code-block:: systemverilog

   genvar i;
   for (i = 0; i < Depth; i++) begin : gen_stage

**Fix**

.. code-block:: systemverilog

   for (genvar i = 0; i < Depth; i++) begin : gen_stage
