.. _backlog:

Backlog
=======

Features that are incomplete, choices that are not yet confirmed, and improvements worth making.
Keep this page up to date: add an entry when something is left out or a limitation is found, and remove it when it is done.
Each entry says what is missing and, where known, what it would take.

Needs confirmation on real installations
----------------------------------------

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
* **Automatic compile order.** Designs without a compile order, such as hdl-modules, need one written by hand. GHDL can
  give one (:code:`ghdl -i` then :code:`--elab-order`); the design section could take :code:`order: auto`.
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
* **More real-world designs** in :code:`scripts/real_world_designs.yaml`: hdl-modules (needs a compile order), surf
  (needs the vendor libraries), and a multi-clock design with vendor clocking.

Lint and rule sets
------------------

* **DO-254 checks still planned for per-file lint**: CP3, CP4, CP6 (reset state and others branch), CP9, CP10, CP14,
  SS5, SS7, SS17 (signals), SS20, SS21, DR2, DR3, DR9, DR10, DR11. See the coverage table of the do254 rule set.
* **Waivers for findings other than clock domain crossings.** Code tags disable a rule on a line; a waiver with a
  required justification, listed in the report, exists only for crossings.
* **Tool qualification support**: :code:`--qualify` running the pass and fail examples of each check of a rule set,
  with a report of expected against actual results and the versions of mhsg, the rule set, GHDL and Yosys.
* **Reproducibility**: reports do not yet record the versions of the tools and the configuration used.
* **Open question**: should lint mode run all style rules by default, or only those of the selected rule set?

Verilog and SystemVerilog
-------------------------

The plan, with the tools evaluated, is in the "Verilog and SystemVerilog" tab of the plan document. Step 1, reading
files with pyslang and running the language neutral rules, is done; see :doc:`../systemverilog`.

* **Style rules (plan step 2 onwards)**: indentation (4 spaces), alignment, naming, keyword and spacing rules after
  the lowRISC style that Verible checks. Until then only whitespace_001, whitespace_002 and the length rules run.
* **Leading tabs** in SystemVerilog files are not reported; in VHDL the indentation rules report them.
* **Inactive** :code:`\`ifdef` **branches and macro arguments** are kept as unclassified tokens (about 5% of the
  tokens of ibex, common_cells and picorv32), so rules about syntax will not see them. Parsing each branch with its
  defines set would let rules check them.
* **Include files and defines from the command line**: files are parsed on their own; a macro defined in another file
  is not expanded, which is fine for style rules but not for lint.
* **Code tags in block comments**: :code:`/* mhsg_off */` is not recognized; only :code:`//` comments are.
* **Lint and design analysis** of SystemVerilog (Verilator, yosys-slang) are later steps of the plan.
* **Real-world SystemVerilog check**: ibex, common_cells and picorv32 (914 files) were checked by hand; they should be
  added to :code:`scripts/real_world_designs.yaml` once it can hold SystemVerilog projects.

Project
-------

* **Documentation warnings.** A few pages have Sphinx warnings that predate this work, such as short title
  underlines in configuring_library_and_package_name_restriction_rules.rst and overview.rst.
