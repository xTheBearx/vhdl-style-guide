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
change. The arguments of macro uses and the code in inactive branches are not parsed, so rules leave them alone, and
spaces next to a macro use are not changed.

Rules
-----

The rules for SystemVerilog are in groups whose names start with :code:`sv_`, see :doc:`rules`. They follow the
`lowRISC Verilog coding style <https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md>`_ that
Verible checks, except that indentation is 4 spaces and lines are 80 characters, as for VHDL. Where a rule checks
what a Verible lint rule checks, its alias is the Verible rule's name.

* :code:`sv_indent_001`: indentation, 4 spaces per level
* :code:`sv_whitespace_001` to :code:`sv_whitespace_015`: the spaces between tokens, as Verible's formatter sets
  them: none before a comma or semicolon, after @ or #, around ++ or after a unary operator, before the parenthesis
  of a call or the bracket of a select; at least one after a comma and around binary and assignment operators; one
  between if, for or case and its parenthesis and around the colon of a block label; at least two before a comment
  at the end of a line
* :code:`sv_blank_line_001`: no blank lines at the end of the file

The rules that apply to every language check SystemVerilog files as well:

* :code:`whitespace_001`: trailing whitespace
* :code:`whitespace_002`: tabs inside a line
* :code:`length_001`: line length, 80 characters by default
* :code:`length_002`: file length
* :code:`length_004`: length of the second line of a statement split over lines

The other rules are VHDL rules and are skipped for SystemVerilog files.

Profiles
########

The **starc** rule set follows the STARC *RTL Design Style Guide for Verilog HDL*: :code:`--rule_set starc` labels
findings with the guide's item numbers and uses its limits, such as lines of 110 characters and 2-space indentation.
See :doc:`lint`.

Indentation
###########

:code:`sv_indent_001` computes the level of each line from the syntax tree. One level in are the members of a
module, package, interface or class; the items of a begin-end block, a function or a task; ports, parameters and
the connections of an instance; enum and struct members; case items; and a statement under if, else, a loop, an
always block or a case item, unless it is a begin-end block. end, else, endmodule and closing brackets are at the
level of what they close.

Not checked: the continuation lines of a statement, lists aligned after their opening bracket (such as the
arguments of a call continued under the first), anything inside an expression, preprocessor directives and code in
inactive :code:`\`ifdef` branches. A comment line continuing the comment at the end of the line above, aligned
with it, keeps that alignment.

Code tags
---------

Code tags, see :doc:`code_tags`, are written in a :code:`//` comment:

.. code-block:: systemverilog

    // mhsg_disable_next_line length_001
    localparam logic [63:0] Seed = 64'h0123_4567_89ab_cdef;  // the seed from the reference model

Configuration
-------------

Rules are configured as for VHDL, see :doc:`configuring`; the same configuration applies to both languages.
