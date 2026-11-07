Release Notes
=============

The releases of MHSG, with their packages, are on `GitHub <https://github.com/xTheBearx/vhdl-style-guide/releases>`_.
The releases of VSG, from which MHSG was forked, are listed `with VSG
<https://github.com/jeremiah-c-leary/vhdl-style-guide/tags>`_.

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
