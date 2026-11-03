.. _systemverilog:

SystemVerilog and Verilog
=========================

MHSG reads SystemVerilog and Verilog files as well as VHDL. Support is being added in steps; this page says what
works now.

Files
-----

A file is read as SystemVerilog when its name ends in :code:`.sv`, :code:`.svh`, :code:`.v` or :code:`.vh`, in any
case. Verilog files are read as SystemVerilog, which is a superset of Verilog. Other files are read as VHDL.
Both kinds can be given in one run:

.. code-block:: bash

  mhsg -f rtl/*.vhd rtl/*.sv --fix

Files are read with `slang <https://github.com/MikePopoloski/slang>`_, through its Python package pyslang, which is
installed with MHSG. The file is kept exactly as written: directives such as :code:`\`define` and :code:`\`ifdef`,
macro uses and the code in inactive :code:`\`ifdef` branches are all kept, and a fix changes only what the rules
change.

Rules
-----

Only the rules that apply to every language run on SystemVerilog files so far:

* :code:`whitespace_001`: trailing whitespace
* :code:`whitespace_002`: tabs inside a line
* :code:`length_001`: line length, 80 characters by default
* :code:`length_002`: file length
* :code:`length_004`: length of the second line of a statement split over lines

The other rules are VHDL rules and are skipped for SystemVerilog files. Rules for SystemVerilog will follow the
`lowRISC Verilog coding style <https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md>`_ that
Verible checks, except that indentation is 4 spaces and lines are 80 characters, as for VHDL.

Tabs at the start of a line are not reported yet; they will be with the indentation rules.

Code tags
---------

Code tags, see :doc:`code_tags`, are written in a :code:`//` comment:

.. code-block:: systemverilog

    // mhsg_disable_next_line length_001
    localparam logic [63:0] Seed = 64'h0123_4567_89ab_cdef;  // the seed from the reference model

Configuration
-------------

Rules are configured as for VHDL, see :doc:`configuring`; the same configuration applies to both languages.
