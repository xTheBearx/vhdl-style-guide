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
* :code:`sv_always_001` to :code:`sv_always_004`: always_comb instead of always @*, blocking assignments in
  always_comb, nonblocking assignments in sequential logic, no mixing of the two in one block
* :code:`sv_case_001`, :code:`sv_case_002`: a default item in every case statement that is not unique, and last
* :code:`sv_statement_001` to :code:`sv_statement_003`: begin-end blocks under if, else, loops, always and initial;
  no consecutive null statements; one statement per line (disabled by default, enabled by the starc rule set)
* :code:`sv_generate_001` to :code:`sv_generate_005`: labelled generate blocks, with labels starting with gen\_
  or g\_; no begin-end blocks directly in generate regions; no generate regions; genvars declared in their loop
* :code:`sv_label_001`: end labels that match their begin labels
* :code:`sv_module_001`, :code:`sv_module_002`: no begin-end blocks directly in a module; no defparam
* :code:`sv_file_001` to :code:`sv_file_004`: files named after their module or package; one module per file
  and relative include paths (disabled by default)
* :code:`sv_naming_001` to :code:`sv_naming_013`: the name styles of Verible (parameters and localparams, enum,
  struct and union types, interfaces, macros and constraints; signals, disabled as in Verible) and no parameter
  starting with disable; the naming rules of the STARC guide (disabled by default): identifier characters, no VHDL
  keywords, no power net prefixes, no names differing only in case, and name lengths
* :code:`sv_literal_001` to :code:`sv_literal_005`: binary literals with a digit for each bit (fixed); values that
  fit their width; and, disabled by default, parameter values with a base, a width on literals wider than 32 bits
  and no comparison with x or z
* :code:`sv_declaration_001`: a type on every parameter
* :code:`sv_function_001` to :code:`sv_function_005`: functions and tasks declared automatic or static (fixed),
  typed arguments, no nonblocking assignments in functions; no tasks (disabled by default)
* :code:`sv_typedef_001`, :code:`sv_typedef_002`: enum, struct and union types declared with typedef
* :code:`sv_dimension_001`, :code:`sv_dimension_002`: packed dimensions as [msb:lsb], unpacked as [0:N-1] or [N]
* rules of the STARC guide, disabled by default: no initial blocks, fork-join or empty branches
  (:code:`sv_statement_004` to :code:`sv_statement_006`), no constant case selector (:code:`sv_case_003`), one event
  control and at most one top-level if or case per always block (:code:`sv_always_005`, :code:`sv_always_006`), no
  synthesis directives in comments (:code:`sv_comment_001`)
* :code:`sv_syntax_001`: code slang cannot parse

The **starc** rule set enables the rules of the STARC guide that are disabled by default.

Lint
####

In lint mode, see :doc:`lint`, slang elaborates each file and analyzes its procedures. :code:`sv_lint_001` to
:code:`sv_lint_010` report what it finds: widths that do not match, latches, multiple drivers, implicit nets,
unused and undriven declarations, duplicate case items and signedness, with slang's own messages; an incomplete
sensitivity list; and any other warning of slang. The **do254** and **starc** rule sets label them with the checks
they implement:

.. code-block:: text

   $ mhsg -f rtl/fifo.sv --lint_only
   WARNING: rtl/fifo.sv(16)DO254-SS4 (sv_lint_002) -- Latch inferred for 'l_o' because it is not assigned on all control paths

A file is elaborated on its own, so the modules, packages and macros of other files are unknown. slang leaves out
the warnings that would follow from them, and mhsg leaves out unused, undriven and implicit signals in a file that
uses anything defined elsewhere, as a signal driven or read there would look undriven or unused.

Syntax errors
#############

Each file is parsed on its own, so macros defined in other files and include files that are not found are not
errors. Other syntax errors are reported by :code:`sv_syntax_001`, and the rules on constructs, from
:code:`sv_always` to :code:`sv_typedef`, skip the file: its syntax tree has constructs missing or misplaced, and
fixing it would be unsafe. The rules on spaces, indentation and lines still check it.

After a fix that changes the structure of the code, such as replacing always @* with always_comb or removing a
generate region, the file is parsed again, so the rules that follow, such as the indentation, see the fixed code.

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
