.. include:: includes.rst

SystemVerilog Label Rules
-------------------------

sv_label_001
############

|phase_1| |error| |structure|

Alias: :code:`sv_label_mismatched`

This rule checks that the label after end matches the label of its begin. An end label without a begin label is
removed.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin : proc_count
   end : proc_counter

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin : proc_count
   end : proc_count
