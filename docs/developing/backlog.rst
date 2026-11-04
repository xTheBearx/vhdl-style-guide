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
* **Netlist checks and declarations of single instances.** design_003 and design_007 follow the path roles of black
  box types; the declarations of single instances name flat paths, which the module graphs do not know. design_006
  counts every black box input as used, since the roles describe clock domains, not which inputs matter.
* **Clears found without a declaration.** A synchronous clear is followed by design_016 when the cdc section lists it
  under clears. Telling clears from resets by structure was tried and dropped: the reset crossing circuits of
  open-logic compute their resets with logic, and were taken for clears.
* **Reset domain crossings into registers without a reset** are not reported by design_018, as their data during a
  reset is not used; a design that relies on such a register right after a reset would need them.
* **Logic depth** counts operators before technology mapping, which is crude; a mapped count would be more realistic
  but slower and loses names.
* **More real-world designs** in :code:`scripts/real_world_designs.yaml`: more of surf, which now analyzes with stub
  vendor packages as its clock manager does, and a design whose clocks come from several vendor clocking primitives.

Lint and rule sets
------------------


Verilog and SystemVerilog
-------------------------

The plan, with the tools evaluated, is in the "Verilog and SystemVerilog" tab of the plan document. Steps 1 to 4
(reading files, style rules, lint and design analysis) are done; see :doc:`../systemverilog`. Step 5, breadth, is
under way: the entries below.

* **Alignment of several columns**: the sv_alignment rules align one column each, such as the names of port
  declarations; Verible also aligns the columns before it, such as the types and packed dimensions.
* **Indentation not checked yet**: continuation lines, lists aligned after their bracket, the contents of
  expressions (multi-line assignment patterns, randomize with blocks), preprocessor directives and inactive
  :code:`\`ifdef` branches. Verible's formatter has rules for each; they need studying before mhsg checks them.
* **Inactive** :code:`\`ifdef` **branches and macro arguments** are kept as unclassified tokens (about 11% of the
  tokens of ibex, common_cells and picorv32, most in the arguments of macros such as :code:`\`ASSERT` and
  :code:`\`uvm_info`), so rules do not check them. Parsing each branch with its defines set, and macro arguments
  that are expressions, would let rules check them.
* **Files with syntax errors** are skipped by the SystemVerilog rules, as a VHDL file that does not parse is. The
  defines and include directories of the systemverilog section let fewer files fall in this case; the real-world
  check runs without them.
* **STARC lint items needing data flow**: about 100 per-file items of the STARC guide, such as widths of function
  arguments, loop bounds, reset polarity and resource sharing, need more than slang's warnings.
* **STARC rule set**: 50 of the 613 items of the STARC guide have rules. The per-file items (216) are planned with
  the SystemVerilog rules, the clock and reset items with design analysis of Verilog designs. The catalogue the set
  was made from records each item's limits and its Verible equivalent, kept in the notes of the set.
* **Sensitivity lists** (sv_lint_008) follow the functions and tasks of the file, not those of packages or other
  files; a variable written inside an if or case before it is read still counts as read.
* **SystemVerilog designs without the yosys-slang plugin**: Yosys' own reader handles Verilog and part of
  SystemVerilog; ibex and common_cells need the plugin, which is not packaged for Ubuntu. Not yet tried with it.
* **Generics of VHDL entities under a Verilog top**: each entity is elaborated once with the defaults of its generics;
  the parameters a Verilog instance sets would need an elaboration of the entity per set of values, under a name of
  its own.
* **Black boxes in Verilog designs with read_slang**: the modules made for black boxes are read with read_verilog
  -lib before the design; whether read_slang links instances to them is not known. Yosys has cell models for Xilinx
  only among the vendors with black box libraries.
* **More SystemVerilog projects** in the real-world check, which runs ibex, common_cells and picorv32: OpenTitan
  (a subset), CVA6, SERV and the sv-tests conformance suite.
