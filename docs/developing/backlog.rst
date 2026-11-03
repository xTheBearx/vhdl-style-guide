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
* **Black box libraries for more primitives.** Transceivers, SERDES (ISERDES, OSERDES), math blocks, Microchip micro
  SRAM, block RAM ECC and cascade ports, and the Intel and Lattice primitives have no declarations yet.
* **Stub declarations without a vendor installation.** Users without vendor tools cannot analyze designs that use
  vendor libraries. A generated stub package, from the black box declarations or from the instantiations, would let
  them.
* **Stand-in models and pragmas for black boxes** (options 4 and 5 of the black box plan): an analysis-only VHDL
  architecture for complex IP, and comment pragmas in component declarations. Not planned unless asked for.
* **Netlist checks and black boxes.** design_002 to design_007 still assume a black box registers its outputs and uses
  all of its inputs; they could use the declarations, as the clock domain checks do.
* **Reconvergence inside black boxes.** What a black box does with its inputs is not known, so only logic before it
  counts. A declaration could say which inputs combine.
* **Reconvergence through clocked resets only.** Synchronous resets that feed two or more registers are not followed
  unless :code:`follow_resets` is set; a finer rule could tell resets from clears.
* **Reset domain crossings through logic** are not checked.
* **Logic depth** counts operators before technology mapping, which is crude; a mapped count would be more realistic
  but slower and loses names.
* **Unused combinational signals and delay chains** (DO-254 SS17 in part, SS1) cannot be found in the netlist, because
  GHDL removes them; they need per-file checks.
* **Unused register detection** parses every VHDL file of the design, which slows large designs (neorv32: about 4 s to
  13 s). Caching the parsed files would help.
* **True dual-port RAM** written from two processes through a shared variable does not synthesize in GHDL
  (Open Logic olo_base_ram_tdp).
* **Generics of type real** are set by patching a copy of the top file; other types GHDL cannot set from the command
  line would need the same.
* **More real-world designs** in :code:`scripts/real_world_designs.yaml`: surf (needs the vendor libraries), the
  hdl-modules designs that use them (hard_fifo), and a multi-clock design with vendor clocking.

Lint and rule sets
------------------

* **DO-254 checks still planned for per-file lint**: CP3, CP4, CP6 (reset state and others branch), CP9, CP10, CP14
  and DR2 for VHDL (checked for SystemVerilog), SS5, SS7, SS17 (signals), SS20, SS21, DR3, DR9, DR10, DR11. See the
  coverage table of the do254 rule set.
* **Tool qualification support**: :code:`--qualify` running the pass and fail examples of each check of a rule set,
  with a report of expected against actual results and the versions of mhsg, the rule set, GHDL and Yosys.

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
* **Double indentation of port and parameter lists**: Verible's formatter indents port declarations, named
  parameters and named ports by its wrap width, twice the indent by default; part of ibex does so. sv_indent_001
  uses one level; an option could allow two.
* **begin on its own line** is put at the level of the statement it belongs to; some code indents it one level more.
* **Inactive** :code:`\`ifdef` **branches and macro arguments** are kept as unclassified tokens (about 11% of the
  tokens of ibex, common_cells and picorv32, most in the arguments of macros such as :code:`\`ASSERT` and
  :code:`\`uvm_info`), so rules do not check them. Parsing each branch with its defines set, and macro arguments
  that are expressions, would let rules check them.
* **Files with syntax errors** are skipped by the SystemVerilog rules, as a VHDL file that does not parse is. The
  defines and include directories of the systemverilog section let fewer files fall in this case; the real-world
  check runs without them.
* **STARC lint items needing data flow**: about 100 per-file items of the STARC guide, such as widths of function
  arguments, loop bounds, reset polarity and resource sharing, need more than slang's warnings.
* **Spaces inside parentheses and braces** and around :code:`) (` between parameter and port lists are not checked;
  Verible's formatter sets them by context.
* **STARC rule set**: 50 of the 613 items of the STARC guide have rules. The per-file items (216) are planned with
  the SystemVerilog rules, the clock and reset items with design analysis of Verilog designs. The catalogue the set
  was made from records each item's limits and its Verible equivalent, kept in the notes of the set.
* **Sensitivity lists** (sv_lint_008) are compared with the names the block reads, by name; reads through
  functions and hierarchical names are not followed.
* **SystemVerilog designs without the yosys-slang plugin**: Yosys' own reader handles Verilog and part of
  SystemVerilog; ibex and common_cells need the plugin, which is not packaged for Ubuntu. Not yet tried with it.
* **Mixed designs with a Verilog top** and VHDL modules: Yosys would need each VHDL entity the Verilog instantiates
  elaborated with the ghdl command first; the design section could list them.
* **Black boxes in Verilog designs with read_slang**: the modules made for black boxes are read with read_verilog
  -lib before the design; whether read_slang links instances to them is not known. Yosys has cell models for Xilinx
  only among the vendors with black box libraries.
* **More SystemVerilog projects** in the real-world check, which runs ibex, common_cells and picorv32: OpenTitan
  (a subset), CVA6, SERV and the sv-tests conformance suite.
