Overview
--------

Multiple HDL Style Guide (MHSG) checks and fixes the coding style of VHDL, Verilog and SystemVerilog files, lints them
against coding standards such as DO-254 and STARC, and analyzes whole designs with GHDL and Yosys, see
:doc:`systemverilog`, :doc:`lint` and :doc:`design_analysis`.

Why MHSG?
#########

MHSG exists to improve `VHDL Style Guide (VSG) <https://github.com/jeremiah-c-leary/vhdl-style-guide>`_ rapidly using
AI. It is a fork of VSG 3.35.0, created by Jeremiah C. Leary: its changes are developed with AI assistance, each backed
by tests and checked against real-world projects. They fix bugs and add rules for open issues of
VSG, and add Verilog and SystemVerilog, lint mode with coding standards, and design analysis.

The style checks keep VSG's reason for being. VSG was created after a code review in which a real issue was masked by
a coding style issue: a finding was created for the style issue, while the real issue was missed until the code was
reviewed again. Depending on the process, a style issue takes a finding to create, disposition, fix and verify.
Spending less time on style leaves more time to review the substance of the code.

Key Benefits
############

* Explicitly define coding standards for VHDL, Verilog and SystemVerilog
* Make coding standards visible to everyone
* Improve code reviews
* Quickly bring code up to current standards
* Find design problems before simulation or synthesis does: latches, loops, clock and reset domain crossings, and
  logic that can never be reached
* Keep the evidence a certification needs: findings labelled with the checks of DO-254 and STARC, waivers with
  justifications, and qualification reports

MHSG allows the style of the code to be defined and enforced over portions or the entire code base.

Key Features
############

* Command line tool

  * Integrates into continuous integration flow tools and pre-commit

* Reports and fixes style issues in VHDL, Verilog and SystemVerilog

  * Horizontal whitespace
  * Vertical whitespace
  * Upper and lower case
  * Indentation and alignment
  * Structure and naming

* Lint mode, with the rule sets do254, do254_plus, starc and cdc

* Design analysis of the whole design, with GHDL and Yosys, and formal checks with SymbiYosys

* Fully configurable rules via JSON/YAML configuration file

  * Disable rules
  * Alter behavior of rules

* Localize rule sets

  * Create your own rules using python
  * Use existing rules as a template
  * Fully integrates into base rule set

Known Limitations
#################

MHSG is a continual work in progress.
As such, this version has the following known limitations:

* Minimal support for embedded PSL
* Parser will not process VHDL 2019

The known gaps are listed in :doc:`developing/backlog`.
