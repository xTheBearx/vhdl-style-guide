.. include:: includes.rst

Verilog and SystemVerilog Blank Line Rules
------------------------------------------

sv_blank_line_001
#################

|phase_3| |error| |blank_line|

Alias: :code:`sv_blank_line_end_of_file`

This rule checks for blank lines at the end of a file, which Verible's formatter removes.

**Violation**

.. code-block:: systemverilog

   endmodule



**Fix**

.. code-block:: systemverilog

   endmodule
