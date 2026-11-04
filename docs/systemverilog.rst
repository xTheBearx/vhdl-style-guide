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

Preprocessor settings
---------------------

The **systemverilog** section of a configuration sets the macros and include directories used when a file is read,
so macros defined in include files expand and :code:`\`ifdef` branches follow the defines:

.. code-block:: yaml

   systemverilog:
     defines:
       SYNTHESIS:
       WIDTH: 8
     include_directories: [rtl/include, vendor/lowrisc_ip/ip/prim/rtl]
     files: [rtl/pkg/*.sv]

A macro with no value is just defined. Without this section, the defines and include directories of the design
section are used, see :doc:`design_analysis`. **files** are compiled with the files of a run in lint mode, such as
packages the checked files use, without being checked themselves; files given with :code:`--index_files` are too.

Rules
-----

The rules for SystemVerilog are in groups whose names start with :code:`sv_`, see :doc:`rules`. They follow the
`lowRISC Verilog coding style <https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md>`_ that
Verible checks, except that indentation is 4 spaces and lines are 80 characters, as for VHDL. Where a rule checks
what a Verible lint rule checks, its alias is the Verible rule's name.

* :code:`sv_indent_001`: indentation, 4 spaces per level
* :code:`sv_indent_002`: continuation lines indented more than the line that starts their statement
* :code:`sv_whitespace_001` to :code:`sv_whitespace_018`: the spaces between tokens, as Verible's formatter sets
  them: none before a comma or semicolon, after @ or #, around ++ or after a unary operator, before the parenthesis
  of a call or the bracket of a select; at least one after a comma and around binary and assignment operators; one
  between if, for or case and its parenthesis and around the colon of a block label; at least two before a comment
  at the end of a line
* :code:`sv_blank_line_001`: no blank lines at the end of the file
* :code:`sv_alignment_001` to :code:`sv_alignment_011`: columns of port declarations, named port and parameter
  connections, declarations, assignments, parameters, case items and struct members, aligned or flush left by how
  the author wrote them, as Verible's formatter infers it; before the names, the types of port declarations after
  their directions and the packed dimensions of declarations, the columns left to right, and the colons inside those
  dimensions, as in :code:`[ 4:0]` under :code:`[31:0]`
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
  synthesis directives in comments (:code:`sv_comment_001`); no falling clock edges, at most 15 outputs and 300 lines
  per always block (:code:`sv_always_007` to :code:`sv_always_009`); no nested conditional operators, if nesting at
  most 7 deep, no change of a loop variable in its loop (:code:`sv_statement_007` to :code:`sv_statement_009`); at
  most 200 case items (:code:`sv_case_004`); packed dimensions numbered from 0 (:code:`sv_dimension_003`); no x or z
  in literals (:code:`sv_literal_006`); ports connected by name (:code:`sv_module_003`); a default value on every
  parameter (:code:`sv_declaration_002`); line comments (:code:`sv_comment_002`); no trailing or double underscores
  in names, and instances named after their module (:code:`sv_naming_014`, :code:`sv_naming_015`); functions that
  read only their arguments and assign no signals, no clock edges in tasks (:code:`sv_function_006` to
  :code:`sv_function_008`); no constants or assigned signals in sensitivity lists, one clock on one edge, active low
  asynchronous resets and at most one per register (:code:`sv_always_010` to :code:`sv_always_014`); if chains
  ending with else, no arithmetic in if conditions, parentheses around mixed && and ||, plain operands of / and %
  (:code:`sv_statement_010` to :code:`sv_statement_013`); no casex or casez, constant case labels and simple
  selectors (:code:`sv_case_005` to :code:`sv_case_007`); one signal per declaration (:code:`sv_declaration_003`);
  include files ending in .h, .vh, .svh or .inc (:code:`sv_file_005`); ports named apart from internal signals
  (:code:`sv_naming_016`); no outputs driven by constants, no gate primitives, no text macros for constants
  (:code:`sv_module_004` to :code:`sv_module_006`); port widths written with parameters (:code:`sv_dimension_004`);
  reset edges matching the polarity tested and every register of a block with reset reset
  (:code:`sv_always_015`, :code:`sv_always_016`); ports ordered clocks, resets, inputs, outputs, inout ports, and no
  text macros inside text macros (:code:`sv_module_007`, :code:`sv_module_008`); a time unit in files with modules
  (:code:`sv_file_006`); constants in conditions with a width, numbers written with a base (:code:`sv_literal_007`,
  :code:`sv_literal_008`); functions ending by assigning their result (:code:`sv_function_009`); fork join blocks
  of at most 5 lines (:code:`sv_statement_014`); a file header giving the module, its function, the author and the
  date (:code:`sv_comment_003`); active low resets named so (:code:`sv_naming_017`); a signal assigned once in a
  sequence of statements and in one procedural block, no registers always assigned one constant, no reset test inside
  a for loop (:code:`sv_always_017` to :code:`sv_always_020`); non-negative integer delays, given only in always
  blocks, plain tri-state enables, no tests of tri-state signals, no repeated branches or conditions in if chains,
  parentheses around chained arithmetic, no arithmetic in the values of ?:, plain signals as indexes, blocking
  assignments in initial blocks, $fstrobe instead of $fdisplay (:code:`sv_statement_015` to
  :code:`sv_statement_025`); no output arguments of tasks (:code:`sv_function_010`); testbench file names
  (:code:`sv_file_007`); a comment for each port and signal, comments in ASCII (:code:`sv_comment_004`,
  :code:`sv_comment_005`); state encodings named and at most 60 states (:code:`sv_case_008`, :code:`sv_case_009`);
  asynchronous resets, made outside the module and without function calls, clocks not read as data, latches without
  reset (:code:`sv_always_021` to :code:`sv_always_025`); at most 500 ports, latches and tri-state buffers in
  modules of their own, no vendor primitives (:code:`sv_module_009` to :code:`sv_module_012`); complete if and case
  statements in functions (:code:`sv_function_011`); bitwise instead of logical operators, merged nested ifs, no
  tests of signals that may be x, no computation on signals in for loops, clock periods as parameters, one clock per
  block, waits on levels in testbenches, simulation tasks between translate_off and translate_on, testbench delays as
  parameters (:code:`sv_statement_026` to :code:`sv_statement_034`); one state machine per module
  (:code:`sv_case_010`); no negative values assigned (:code:`sv_literal_009`);
  with the widths of slang's elaboration of the file: 1-bit operands of logical operators and conditions, comparisons
  of operands of one width, values not narrower than their targets, targets wide enough for sums and products,
  dividers and multipliers of limited width, no reductions in wider contexts and no comparisons of integers with
  vectors (:code:`sv_statement_035` to :code:`sv_statement_043`);
  short top-level names that differ in more than case, no names of library cells, clock and reset base names
  (:code:`sv_naming_018` to :code:`sv_naming_020`); macros undefined in their module, synchronously reset registers,
  hierarchy and connections in modules of their own and in port order, registered outputs (:code:`sv_module_013` to
  :code:`sv_module_017`); unit delays on register assignments (:code:`sv_always_026`); small case tables and grouped
  wildcards (:code:`sv_case_011`, :code:`sv_case_012`); no priority logic in loops, short loops with comparisons, no
  mixed signedness, one arithmetic operation per line, common expressions computed once, stimulus offset from clock
  edges, shared expressions in signals (:code:`sv_statement_044` to :code:`sv_statement_050`); numbers named with
  parameters (:code:`sv_literal_010`); a history in the file header and enough comments (:code:`sv_comment_006`,
  :code:`sv_comment_007`)
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

The SystemVerilog files of a run are compiled together, once, with the files of the systemverilog section and of
:code:`--index_files`, so each file is checked against the others: an instance against the ports of its module, a
package against the files that use it. A file that still uses a module, package or macro the run does not know is not
checked for unused, undriven and implicit signals, as a signal driven or read there would look undriven or unused.
With :code:`--fix`, the files are fixed first and compiled together again, so the files the fixes changed are still
checked against the others.

**Verilator.** When Verilator is installed, it lints the files of the run too (:code:`verilator --lint-only -Wall`),
and three rules report the warnings of the checks slang does not make: :code:`sv_lint_012` signals assigned in
always blocks of different clocks (MULTIDRIVEN), :code:`sv_lint_013` case statements that do not cover every value (CASEINCOMPLETE),
and :code:`sv_lint_011` the others, such as blocking assignments in clocked processes (BLKSEQ) and non-blocking ones
in combinational processes (COMBDLY); its **verilator_warnings** option lists them. The **do254** rule set labels
:code:`sv_lint_012` with SS6 and :code:`sv_lint_013` with SS2, and **starc** :code:`sv_lint_013` with 2.8.1.6.
Verilator runs only when one of the three rules is enabled: in lint mode without a rule set
(:code:`--lint --rule_set none`), with a rule set that lists one, or when the configuration enables one:

.. code-block:: yaml

   rule:
     sv_lint_011:
       disable: false
   systemverilog:
     verilator: /opt/verilator/bin/verilator   # optional: the program, or false to not run Verilator

Verilator needs every module and package a file uses. Files defining packages are given to it first; a module the run
instantiates but does not define gets an empty stub with the ports and parameters its instances name. Files slang
cannot parse, files importing a package the run does not define, such as uvm_pkg, and files Verilator stops at, such
as one using a construct it does not support, are left out, and a warning on standard error says how many.

.. code-block:: text

   $ mhsg -f rtl/*.sv --lint_only -c project.yaml

With :code:`--fix`, a file the fixes changed is compiled again on its own, as the warnings of the run describe the
file before the fixes.

Syntax errors
#############

Each file is parsed on its own, so macros defined in other files and include files that are not found are not
errors. Other syntax errors are reported by :code:`sv_syntax_001`, and the SystemVerilog rules skip the file: its
syntax tree has constructs missing or misplaced, and its tokens may be classified wrongly near the errors, so checking
or fixing it would be unsafe. Only the rules for every language, on trailing spaces, tabs and lengths, and
:code:`sv_blank_line_001` still check it.

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

The continuation lines of a statement have no level: :code:`sv_indent_002` checks only that they are indented more
than the line that starts the statement, so lists aligned after their opening bracket (such as the arguments of a
call continued under the first) are kept. A line starting with a closing bracket, with the opening bracket of a port
list, with the next expression of a case item, or after an attribute on a line of its own may be at the level of
the statement. Its fix follows the continuation line before it, or indents by :code:`continuation_indent` levels, 2
by default, as Verible's formatter does with its wrap width. Not checked: preprocessor directives, code in inactive
:code:`\`ifdef` branches and lines after a macro call, whose arguments are not parsed. A comment line continuing the
comment at the end of the line above, aligned with it, keeps that alignment.

Code tags
---------

Code tags, see :doc:`code_tags`, are written in a :code:`//` comment:

.. code-block:: systemverilog

    // mhsg_disable_next_line length_001
    localparam logic [63:0] Seed = 64'h0123_4567_89ab_cdef;  // the seed from the reference model

Configuration
-------------

Rules are configured as for VHDL, see :doc:`configuring`; the same configuration applies to both languages.
