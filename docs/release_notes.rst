Release Notes
=============

The releases of MHSG, with their packages, are on `GitHub <https://github.com/xTheBearx/vhdl-style-guide/releases>`_.
The releases of VSG, from which MHSG was forked, are listed `with VSG
<https://github.com/jeremiah-c-leary/vhdl-style-guide/tags>`_.

4.0.3
-----

**Design analysis**

* The bits of a vector input can be declared independent signals: :code:`cdc: inputs: {d_i: {domain: async, bits:
  independent}}`. Each bit is then a signal of its own, with its own reconvergence tag, so design_009 does not take
  the bits as one bus synchronized bit by bit; two of them combined after their synchronizers are still reported by
  design_016. :code:`bits: bus` is the default, the meaning of a plain :code:`d_i: async`. The crossing report lists
  the declared inputs. An input given as anything but a domain or such a map, which was silently left unchecked, is
  now a configuration error. (`#92 <https://github.com/xTheBearx/vhdl-style-guide/issues/92>`_)

**DO-254 checks**

* DR9, consistent signal names across the hierarchy (lint_040 for VHDL, sv_module_018 for Verilog and SystemVerilog),
  no longer checks the ports of a unit instantiated more than once in the run, whose connections cannot all carry the
  port's names, and the two rules share one comparison of names: one prefix and one suffix removed, the active-low
  suffixes such as :code:`_n_i` among them, so :code:`rst_n_i => rst_n` matches. A different name is still reported.
  (`#93 <https://github.com/xTheBearx/vhdl-style-guide/issues/93>`_)
* PORT, no inout ports (lint_019, sv_module_020), leaves out the top level: the unit the design section names as
  :code:`top`, or, in lint mode with more than one file or with index files, a unit nothing in the run instantiates.
  A file checked alone without index files has its inout ports reported, as before.
  (`#94 <https://github.com/xTheBearx/vhdl-style-guide/issues/94>`_)
* CP3, numbers named (sv_literal_010), no longer reports parameter value assignments of instances, named or ordered,
  like parameter declarations, and checks the statements of every case item alike, :code:`default` included, as
  lint_034 does for VHDL. A number in the statement of a numbered case item, which was missed, is now reported.
  (`#95 <https://github.com/xTheBearx/vhdl-style-guide/issues/95>`_)

4.0.2
-----

**DO-254 checks for SystemVerilog**

* The do254 and do254_plus rule sets name SystemVerilog rules for every per-file check they can test, and say which
  checks are VHDL only. Nineteen new rules cover the checks no rule tested, among them registers without a reset
  (sv_always_027), unlabelled always blocks (sv_always_029), reads before assignment (sv_always_030, sv_always_031),
  states never entered or never left (sv_case_013), unconnected instance ports (sv_lint_017, sv_lint_018), signals
  renamed at a port (sv_module_018) and requirement tags (sv_comment_010). The coverage pages and qualification suites
  are regenerated with SystemVerilog examples.
* sv_case_013 finds the state machines whose enum type another file of the run declares, such as a package.

**DO-254 rule sets and style**

* The do254 and do254_plus rule sets set the style rules their checks need, so fixing the style no longer undoes a
  check: labels are kept (DR1), the comments that count towards the share are kept (DR11), generic maps are upper case
  (NAMES), instantiations name the entity (ENTITY), and a requirement tag may sit directly above its entity (REQ). An
  option of your own that contradicts a check still wins and is reported once at the start of the run. lint_042 rounds
  the comment share down. (`#90 <https://github.com/xTheBearx/vhdl-style-guide/issues/90>`_)

**Fixes**

* One configuration serves VHDL, Verilog and SystemVerilog files: rules of another language, and the SystemVerilog
  only rules for a file read as Verilog-2005, are left out for that file; a name that is no rule of any language is
  still an error. (`#89 <https://github.com/xTheBearx/vhdl-style-guide/issues/89>`_)
* design_009 accepts a synchronizer fed straight from an input port declared async; a port through a gate is still
  logic before the synchronizer. (`#91 <https://github.com/xTheBearx/vhdl-style-guide/issues/91>`_)
* A hierarchical call such as u_report.check() is no longer taken for a package, which left the file out of
  Verilator's lint. (`#88 <https://github.com/xTheBearx/vhdl-style-guide/issues/88>`_)
* An install from a git tag with uv reports the tag as its version, such as 4.0.2, instead of
  4.0.1.post0+git.<sha>.dirty: the marker file uv leaves in its checkout is ignored.

4.0.1
-----

**Verilog and SystemVerilog**

* Verilog files, :code:`.v` and :code:`.vh`, are read as Verilog-2005, no longer as SystemVerilog: names that are
  keywords only in SystemVerilog, such as logic and bit, are names, and the 15 rules that need SystemVerilog, such as
  sv_always_001 asking for always_comb, are not applied to them. The rules that apply to both give Verilog files advice
  they can follow, such as always @* in the finding of sv_lint_008, and their fixes keep the file Verilog-2005; see
  :doc:`verilog_2005` for each rule. Verilator and Yosys read the files the same way.
* **v_files: systemverilog** in the systemverilog section of the configuration reads :code:`.v` and :code:`.vh` files
  as SystemVerilog, as before, for projects that write SystemVerilog in them.
* Verilator 5 lints the timing controls of testbenches, such as an event control in an initial block, with
  :code:`--timing`, instead of leaving such files out; an older Verilator gets neither timing option.

4.0.0a1
-------

The first release of MHSG, an alpha: a fork of VHDL Style Guide (VSG) 3.35.0 that keeps the style rules of VSG and
adds lint checks, design analysis of the whole design, and Verilog and SystemVerilog. MHSG exists to improve VSG
rapidly using AI; its changes are developed with AI assistance, each backed by tests and checked against real-world
projects.

As an alpha, it is ready to try, not to rely on: rules, their names and options, the configuration and the reports may
still change, and it is not yet on PyPI. Please report what you find at
https://github.com/xTheBearx/vhdl-style-guide/issues.

**Changes that need attention when moving from VSG**

* The tool and its package are named mhsg. The ``vsg_`` code tags of existing files are still recognized.
* The default indent is 4 spaces and the default line length 80.
* The project is managed with uv and needs Python 3.12 or later.

**Lint mode**

* ``--lint`` and ``--lint_only`` run lint checks that report design problems such as latches, labelled with the checks
  of a rule set: DO-254 (do254, do254_plus), STARC and CDC. Findings have the severities Error, Warning and Note, can be
  waived with a justification, and are listed with the tools and configuration in the reports.
* The STARC rule set covers 273 of the 613 items of the STARC RTL Design Style Guide with rules; every other item is
  marked for review, with the reason.
* ``--qualify`` runs the qualification suite of a rule set and writes a tool qualification report.

**Design analysis**

* ``--design`` elaborates the design with GHDL and Yosys and checks it as a whole, with design_001 to design_048:
  latches, combinational loops, multiple drivers, constant and unused registers, logic depth, clock domain crossings,
  reconvergence, generated and gated clocks and resets, reset domain crossings, tri-state buses, memories, hierarchy
  and block structure, and design for test with the test_mode and scan_shift inputs held.
* Black boxes are declared with roles or archetypes, with libraries for AMD Xilinx, Microchip, Altera and Lattice
  primitives.
* Reset domain crossings that an isolation signal keeps from capturing are recognized when the isolation is declared
  in the cdc section, with a justification; the others name the signals that would isolate them.
* With SymbiYosys: branches that can never be taken from reset (design_025), states of state machines never entered
  (design_047), and state machines that never return to their reset state (design_048).

**Verilog and SystemVerilog**

* Verilog and SystemVerilog files are formatted and checked with rules for indentation, whitespace, blank lines,
  alignment, structure, naming, literals, declarations and comments, also in inactive ``ifdef`` branches and macro
  bodies, and linted with slang and, optionally, Verilator, the files of a run compiled together.
* Design analysis reads Verilog, SystemVerilog and mixed designs, with the yosys-slang plugin for SystemVerilog.
* The pre-commit hook checks Verilog and SystemVerilog files as well as VHDL ones.

**Issues of VSG**

* Rules for issues of VSG: blank lines of generic and port maps (#1447), subprogram instantiations (#1365), consistent
  case in packages (#1384), package prefixes and suffixes (#690), the file_rules configuration (#593), a second line
  length rule (#1551), the order of generics (#1509), commented-out code (#607) and descriptive rule aliases (#1529).

**Known limitations**

* The VHDL parser does not process embedded PSL or VHDL-2019.
* The formal rules can leave branches and states undecided within their time limits.
* The black box libraries of the vendors were written from their guides, without a vendor installation to check the
  port names against.
* The known gaps are listed in :doc:`developing/backlog`, and the bugs found in the tools MHSG depends on in
  :doc:`developing/dependency_issues`.
