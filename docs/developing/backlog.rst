.. _backlog:

Backlog
=======

Features that are incomplete, choices that are not yet confirmed, and improvements worth making.
Keep this page up to date: add an entry when something is left out or a limitation is found, and remove it when it is done.
Each entry says what is missing and, where known, what it would take.
Bugs and limitations of the tools MHSG uses, and how MHSG works around them, are in :doc:`dependency_issues`.

Deferred: needs confirmation on real installations
--------------------------------------------------

Deferred for now: these need Vivado and Libero installed.

* **Vendor declaration file locations.** The locations :code:`vendor_libraries` searches for AMD/Xilinx, Microchip,
  Intel and Lattice follow the vendors' documented layouts but were never checked against a real installation.
  Run once with Vivado and with Libero installed, and correct the locations if needed.
* **Declaration libraries.** The :code:`xilinx` and :code:`microchip` black box libraries were written from the
  vendors' libraries guides and tested with hand-written stand-in declarations. Check the port names against real
  vendor files; the Microchip names, including those of the cores Libero generates, are the less certain.
* **Real vendor files with GHDL.** Whether GHDL analyzes the real :code:`unisim_VCOMP.vhd`, the XPM package and the
  Microchip family packages without options is not known.

Design analysis
---------------

* **Formal reachability (plan step 6).** Cover checks per branch and state with SymbiYosys, assumptions, time budgets
  and three-way results. SymbiYosys is not packaged for Ubuntu; it needs the YosysHQ OSS CAD Suite.
* **Black box libraries for more primitives.** Transceivers, PCIe and memory interface cores have no declarations;
  the Intel and Lattice libraries cover the common primitives only. The names of the Intel megafunctions could not be
  checked against cell models, as Yosys has none for them.
* **Stand-in models and pragmas for black boxes** (options 4 and 5 of the black box plan): an analysis-only VHDL
  architecture for complex IP, and comment pragmas in component declarations. Not planned unless asked for.
* **Netlist checks and declarations of single instances.** design_003 and design_007 check each module once, so a
  declaration of single instances applies only when it applies to every instance of the cell in the design. design_006
  counts every black box input as used, since the roles describe clock domains, not which inputs matter.
* **Clears found without a declaration.** A synchronous clear is followed by design_016 when the cdc section lists it
  under clears. Telling clears from resets by structure was tried and dropped: the reset crossing circuits of
  open-logic compute their resets with logic, and were taken for clears.
* **Reset domain crossings into registers without a reset** are not reported by design_018, as their data during a
  reset is not used; a design that relies on such a register right after a reset would need them.
* **Logic depth after mapping** (design_019) reports only the longest path of the design, at its top, as mapping
  renames the signals in between; each path, with names, would need a mapping that keeps them, such as abc's with
  the -dff and -keepff options, and a report of the path from the timing of the device.
* **More real-world designs** in :code:`scripts/real_world_designs.yaml`: more of surf, which now analyzes with stub
  vendor packages as its clock manager does, and a design whose clocks come from several vendor clocking primitives.

Lint and rule sets
------------------


Verilog and SystemVerilog
-------------------------

The plan, with the tools evaluated, is in the "Verilog and SystemVerilog" tab of the plan document. Steps 1 to 4
(reading files, style rules, lint and design analysis) are done; see :doc:`../systemverilog`. Step 5, breadth, is
under way: the entries below.

* **Alignment inside packed dimensions**: sv_alignment_010 aligns the opening brackets of packed dimensions; Verible
  may also pad inside the brackets, as in :code:`[ 4:0]` under :code:`[31:0]`, which is not checked.
* **Indentation not checked yet**: the exact indent of continuation lines (sv_indent_002 checks only that they are
  indented more than their statement), the contents of expressions (multi-line assignment patterns, randomize with
  blocks), preprocessor directives and inactive :code:`\`ifdef` branches. Verible's formatter has rules for each;
  they need studying before mhsg checks them.
* **Inactive** :code:`\`ifdef` **branches and macro arguments** are kept as unclassified tokens (about 11% of the
  tokens of ibex, common_cells and picorv32, most in the arguments of macros such as :code:`\`ASSERT` and
  :code:`\`uvm_info`), so rules do not check them. Parsing each branch with its defines set, and macro arguments
  that are expressions, would let rules check them.
* **Files with syntax errors** are skipped by the SystemVerilog rules, as a VHDL file that does not parse is. The
  defines and include directories of the systemverilog section let fewer files fall in this case; the real-world
  check runs without them.
* **STARC items with judgement**: resource sharing, Gray encoding of states and the like are left to review; the rules
  on loop bounds and common expressions compare the code as written, so loop bounds given by parameters, and
  expressions written differently, are not checked.
* **STARC rule set**: 218 of the 613 items of the STARC guide have rules, the design rules among them for the items
  on loops, drivers, generated and gated clocks and resets. Every per-file item has a rule or is left to review
  (status manual, with the reason in its note). The 57 items with status design need what design analysis does not
  have: gate counts of hierarchy levels, the test modes of design for test, hierarchy identification characters,
  and which memories and I/O cells a design uses. The catalogue the set
  was made from records each item's limits and its Verible equivalent, kept in the notes of the set.
* **SystemVerilog designs without the yosys-slang plugin**: Yosys' own reader handles Verilog and part of
  SystemVerilog; ibex and common_cells need the plugin, which is not packaged for Ubuntu. Not yet tried with it.
* **Generics of VHDL entities under a Verilog top** are passed on when they are literals and the instance is in a
  module without parameters; expressions of parameters, and instances in modules that have parameters, would need the
  elaboration of the Verilog first, as read_slang does.
* **Black boxes in Verilog designs with read_slang**: the modules made for black boxes are read with read_verilog
  -lib before the design; whether read_slang links instances to them is not known. Yosys has cell models for Xilinx
  only among the vendors with black box libraries.
