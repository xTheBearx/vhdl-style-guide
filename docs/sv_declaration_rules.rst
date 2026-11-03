.. include:: includes.rst

SystemVerilog Declaration Rules
-------------------------------

sv_declaration_001
##################

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_declaration_explicit_parameter_storage_type`

This rule checks that parameters and localparams are declared with a type, such as int or logic [7:0], as
Verible's explicit-parameter-storage-type rule does.

**Violation**

.. code-block:: systemverilog

   parameter Depth = 8;

**Fix**

.. code-block:: systemverilog

   parameter int Depth = 8;
