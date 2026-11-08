.. _backlog:

Backlog
=======

Features that are incomplete, choices that are not yet confirmed, and improvements worth making.
Keep this page up to date: add an entry when something is left out or a limitation is found, and remove it when it is done.
Each entry says what is missing and, where known, what it would take.
Bugs and limitations of the tools MHSG uses, and how MHSG works around them, are in :doc:`dependency_issues`.
Simulation on a CUDA GPU is planned in :doc:`gpu_simulation`, not started.

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

* **Liveness under fair inputs.** design_025 checks branches, design_047 the states of state machines and design_048
  that each state machine can return to its reset state, with SymbiYosys. That a machine always returns, whatever its
  inputs do once they are fair, such as an acknowledge that eventually comes, needs fairness assumptions of the design;
  SymbiYosys checks such properties in live mode, with suprove. States reached only after a clock divider or a long
  counter are undecided within the time limits: the checks could start from states found by simulation, or abstract
  counters. SymbiYosys is not packaged for Ubuntu: CI runs the formal rules in the design-oss job, with the OSS CAD
  Suite.
* **Black box libraries for more primitives.** The transceivers of Intel and Microchip, and memory controllers, are
  IP cores whose names the vendor tools choose: they are declared with the transceiver and memory_controller
  archetypes, not in libraries. The Intel and Lattice libraries cover the common primitives and the ECP5 SERDES. The
  timing of the ports of the Xilinx transceivers and PCI Express blocks, and of the ECP5 SERDES, was taken from the
  user guides without a vendor installation to check it against. The names of the Intel megafunctions could not be
  checked against cell models, as Yosys has none for them.
* **Stand-in models and pragmas for black boxes** (options 4 and 5 of the black box plan): an analysis-only VHDL
  architecture for complex IP, and comment pragmas in component declarations. Not planned unless asked for.
* **Inputs of black boxes counted as used**: design_006 counts the inputs of a black box as used when one of its
  outputs is, or when it has none, such as a debug core. Which inputs an output depends on is not declared, so all
  inputs of a box with a used output count as used.
* **Clears found without a declaration.** A synchronous clear is followed by design_016 when the cdc section lists it
  under clears. Telling clears from resets by structure was tried and dropped: the reset crossing circuits of
  open-logic compute their resets with logic, and were taken for clears.
* **Reset domain crossings into registers without a reset** are not reported by design_018, as their data during a
  reset is not used; a design that relies on such a register right after a reset would need them.
* **Reset domain crossings through black boxes**: the outputs of a black box with a declared reset are not sources of
  reset domain crossings, and its inputs are not destinations.
* **Isolation checked in time**: design_018 checks that a declared isolation keeps the destination from capturing, not
  that it takes its value before the source reset is asserted; for a reset that the design asserts itself, such as
  from a reset controller, SymbiYosys could prove the order.
* **More real-world designs** in :code:`scripts/real_world_designs.yaml`: surf's designs with SimpleDualPortRam wait
  for GHDL, see :doc:`dependency_issues`, and its transceiver wrappers need the Xilinx IP cores they instantiate.

Lint and rule sets
------------------


Verilog and SystemVerilog
-------------------------

The plan, with the tools evaluated, is in the "Verilog and SystemVerilog" tab of the plan document. Steps 1 to 4
(reading files, style rules, lint and design analysis) are done; see :doc:`../systemverilog`. Step 5, breadth, is
under way: the entries below.

* **Indentation not checked yet**: continuation lines are checked to be indented more than their statement, and fixed
  by **continuation_indent** levels; continuation lines indented more, such as arguments aligned after their bracket,
  are not checked. Assignment patterns, call arguments and randomize with constraints whose opening bracket ends
  its line are checked by sv_indent_004, as Verible lays them out; the other ways Verible breaks lines, such as a
  call on the right of a blocking assignment, which it lays out in several ways, are not.
* **Code the syntax tree does not have**: the code of inactive :code:`\`ifdef` branches is classified from parses with
  the macros of their conditions switched, at most 8 of them, and the arguments of macro uses where the macros place
  them, so rules check both. The lint rules lint the code of inactive branches in the file on its own with the
  macros switched, and report the warnings in the code macro arguments expand to at the arguments; the other rules
  that read the syntax tree do not see either, and macro arguments are not indented by sv_indent_001. The bodies of
  macro definitions are classified where the first use of each macro in the file places them, and checked but for
  their indentation; the bodies of macros the file does not use are not checked.
* **Files with syntax errors** are checked and fixed but for the part of each item of a design unit with an error,
  from the line of the error to the end of the item, where slang's syntax tree may be wrong; for an error outside the
  items, such as in the header of a module, the rest of the unit. Checking that part too would need slang's recovery
  inside an item to be trusted.
* **STARC items with judgement**: resource sharing, Gray encoding of states and the like are left to review; the rules
  on loop bounds and common expressions compare the code as written, so loop bounds given by parameters, and
  expressions written differently, are not checked.
* **STARC rule set**: 273 of the 613 items of the STARC guide have rules, the design rules among them for the items
  on loops, latches, drivers, tri-state buses, memory outputs and placement, clock domains per block, generated and
  gated clocks and resets and where they are made, black boxes on clocks and resets, the contents of the top level,
  I/O cells, gates per module, clocks, latches and pins in test mode, hierarchy IDs and paths across blocks. Every
  other item is left to review (status manual, with the reason in its note): synthesis and timing scripts, design
  management and judgement. Items on speed-critical paths are checked on all paths, as design analysis has no timing;
  the minimum gates of a basic block is not checked. The catalogue the set was made from records each item's limits
  and its Verible equivalent, kept in the notes of the set.
* **SystemVerilog designs without the yosys-slang plugin**: Yosys' own reader handles Verilog and part of
  SystemVerilog, and the plugin is not packaged for Ubuntu; design analysis says so when the reader fails, and the
  tools of the design section, or MHSG_YOSYS, name a Yosys that has it, such as that of the OSS CAD Suite. ibex_core
  and the gray-code CDC FIFO of common_cells are checked with it in the design-oss job of CI. Converting the files
  with sv2v for Yosys' own reader was not tried: sv2v could not be fetched where mhsg was developed.
