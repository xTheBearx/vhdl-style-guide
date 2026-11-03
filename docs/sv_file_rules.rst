.. include:: includes.rst

SystemVerilog File Rules
------------------------

sv_file_001
###########

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_file_module_filename`

This rule checks a file holding modules is named after one of them, as Verible's module-filename rule does:
counter.sv holds module counter.

**Violation**

.. code-block:: systemverilog

   // file fifo_top.sv
   module fifo;

**Fix**

.. code-block:: systemverilog

   // file fifo.sv
   module fifo;

sv_file_002
###########

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_file_package_filename`

This rule checks a file holding a package is named after it, as Verible's package-filename rule does:
fifo_pkg.sv holds package fifo_pkg.

**Violation**

.. code-block:: systemverilog

   // file types.sv
   package fifo_pkg;

**Fix**

.. code-block:: systemverilog

   // file fifo_pkg.sv
   package fifo_pkg;

sv_file_003
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_file_one_module_per_file`

This rule checks a file holds at most one module, as the STARC guide asks (1.1.1.1). It is disabled by
default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo;
   endmodule
   module fifo_ram;
   endmodule

**Fix**

.. code-block:: systemverilog

   module fifo;
   endmodule

sv_file_004
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_file_include_relative_path`

This rule checks that include directives name files by relative paths, as the STARC guide asks (3.2.2.4). It
is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   `include "/home/user/rtl/defines.svh"

**Fix**

.. code-block:: systemverilog

   `include "defines.svh"
