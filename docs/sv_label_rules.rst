.. include:: includes.rst

Verilog and SystemVerilog Label Rules
-------------------------------------

sv_label_001
############

|phase_1| |error| |structure|

Alias: :code:`sv_label_mismatched`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

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
