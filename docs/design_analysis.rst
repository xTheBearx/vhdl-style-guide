.. _design_analysis:

Design Analysis
===============

Lint mode checks one file at a time.
Design analysis checks the whole elaborated design: it runs GHDL and Yosys on the design and reports what they find
at the lines of the VHDL files, in the same output formats as the other checks.

It finds problems a single file cannot show, for example a latch inferred from a case statement on an enumerated type
declared in a package, or one that exists only for some values of the generics.

Requirements
------------

Design analysis needs `GHDL <https://github.com/ghdl/ghdl>`_, `Yosys <https://github.com/YosysHQ/yosys>`_
and the GHDL plugin for Yosys, for example from the packages ghdl, yosys and yosys-plugin-ghdl,
or from the `OSS CAD Suite <https://github.com/YosysHQ/oss-cad-suite-build>`_.
All three must be on the path.

The plugin does not always find the libraries of the installed GHDL backend.
MHSG sets **GHDL_PREFIX** to the library directory GHDL reports, unless it is already set.

Describing the design
---------------------

The design is described in the **design** section of a configuration file:

.. code-block:: yaml

   design:
     top: fifo_top
     standard: "08"
     libraries:
       - name: common
         files_from: ip/common_files.f
       - name: work
         files:
           - src/fifo_pkg.vhd
           - src/*.vhd
         exclude: ["*_tb.vhd"]
     generics:
       DEPTH: 16
       CLOCK_HZ: 100.0e6
     ghdl_options: [-frelaxed-rules]

* **top** is the top entity, and **architecture** optionally its architecture.
* **standard** is the VHDL standard, one of 87, 93, 93c, 00, 02, 08 (the default) or 19.
* **libraries** lists the libraries in the order they are analyzed, each with a **name** and its files.
  **files** lists files and glob patterns; the files of a pattern are sorted, and the order of the list is kept.
  **files_from** names a file which lists one file per line. Lines starting with # or // are comments,
  environment variables are expanded, and relative paths are relative to the list file.
  **exclude** lists patterns of files to leave out, such as testbenches or files of a missing submodule.
* **top_library** is the library of the top entity, by default the last library.
* **generics** sets generics of the top entity: numbers, booleans, strings, and vectors as bits, such as ``"00000111"``.
  Every generic without a default value must be set, and every generic set must exist; otherwise design_001 reports
  it before GHDL runs, since GHDL would quietly use the leftmost value of the type, such as 1 for a positive.
  GHDL cannot set a generic of type real from the command line, so MHSG analyzes a copy of the file of the top entity
  in which the value is the default. Findings still name the original file, at the same lines.
* **ghdl_options** are passed to GHDL, for example :code:`-fsynopsys` for designs which use the Synopsys packages.
* **work_directory** keeps the files of GHDL and Yosys, such as the Verilog and the JSON netlist, in a directory,
  for a closer look. Without it they are written to a temporary directory and removed.

Paths in the configuration may use environment variables.

Running design analysis
-----------------------

.. code-block:: bash

   mhsg --design -c design.yaml

Design analysis runs instead of the style checks, so files are not needed on the command line.
With **--lint**, findings are labelled with the checks of the rule set and reported with their severities,
the same as in lint mode:

.. code-block:: text

   $ mhsg --design --lint -c design.yaml -of syntastic
   WARNING: src/latch.vhd(17)DO254-SS4 (design_002) -- Synthesis infers a latch for q in latch_top

The exit status is 1 if a step fails or a finding has the error severity, otherwise 0.

How it works
------------

1. GHDL analyzes the files of each library, in order.
2. GHDL synthesizes the top entity to Verilog, which is only read for the source locations GHDL writes in it.
3. Yosys synthesizes the same top entity through the GHDL plugin and writes the netlist before any optimization.
4. The design rules check the result. Each cell of the netlist is located in the VHDL by joining its name to the
   location in GHDL's Verilog, and a latch is reported at the assignment that infers it.

Analysis stops at the first step that fails, and design_001 reports the errors.
The other design rules need the netlist, so they run once the design analyzes and elaborates.

Design rules
------------

* :code:`design_001` reports the errors of GHDL, such as wrong types, names that are not declared and ranges that do
  not match, and generics of the top entity that need a value (DO-254 CP1, CP7, CP13).
* :code:`design_002` reports latches (DO-254 SS4).
* :code:`design_003` reports combinational loops, also through several processes and instances (DO-254 SS3).
* :code:`design_004` reports signals with more than one driver, such as two instances driving one signal (DO-254 SS6).
* :code:`design_005` reports registers that never change (DO-254 SS18).
* :code:`design_006` reports registers that are never used and signals that are read but never assigned (DO-254 SS17).
* :code:`design_007` reports combinational paths deeper than :code:`maximum_depth` logic levels, 48 by default (DO-254 SS19).

* :code:`design_008` to :code:`design_016` check clock domain crossings, clocks and resets, see below.

See :doc:`design_rules`. Design rules are configured like other rules, for example with a different severity:

.. code-block:: yaml

   rule:
     design_007:
       maximum_depth: 32

Each entity is checked on its own netlist, before the netlist is flattened or optimized, so findings point at the
entity that holds the logic. Paths through instances use a summary of the instantiated entity: which inputs reach
which outputs without a register, which inputs it uses, and its logic depths.

Clock domain crossings
----------------------

Clock domain crossing analysis runs on the whole design, flattened: every instance is replaced by its logic, so a
crossing is found wherever it is in the hierarchy.

**Clocks.** The clock of each register is traced back through buffers and inverters to its source: an input port,
a black box output such as a PLL, a register, which divides a clock, or logic, which gates a clock.
Each source is a clock domain, asynchronous to every other unless they are grouped.
A divided or gated clock belongs with the clock it comes from.

**Crossings.** The data inputs of each register are traced back through logic to the registers that drive them.
A register of another, asynchronous domain is a crossing, classified as:

+--------------------------------+---------------------------------------------------------------------------------+
| Status                         | Meaning                                                                         |
+================================+=================================================================================+
| synchronized                   | Captured directly by two or more registers in series, each feeding only the     |
|                                | next.                                                                           |
+--------------------------------+---------------------------------------------------------------------------------+
| gray-coded bus                 | The bits of a bus synchronized one by one, loaded with the gray code of a       |
|                                | value, so only one bit changes at a time.                                       |
+--------------------------------+---------------------------------------------------------------------------------+
| qualified by enable            | Data held stable and captured when an enable synchronized to the destination    |
|                                | clock allows it, as in a handshake.                                             |
+--------------------------------+---------------------------------------------------------------------------------+
| bus synchronized bit by bit    | Several bits of one register synchronized one by one: they can arrive in        |
|                                | different cycles. Reported by design_009.                                       |
+--------------------------------+---------------------------------------------------------------------------------+
| logic before synchronizer      | Logic between the domains feeds the first stage and can glitch. Reported by     |
|                                | design_009.                                                                     |
+--------------------------------+---------------------------------------------------------------------------------+
| unsynchronized                 | Captured by a single register, or used through an enable or reset. Reported by  |
|                                | design_008.                                                                     |
+--------------------------------+---------------------------------------------------------------------------------+
| waived                         | Waived in the design section, with a justification.                             |
+--------------------------------+---------------------------------------------------------------------------------+

**Reconvergence.** Signals synchronized separately from one clock domain can arrive in different cycles of the
destination clock. A register whose inputs combine two or more of them, through logic of its own domain, can see a
state the source never had; design_016 reports it. The bits of one bus count as one signal, since a gray-coded bus is
meant to be combined and design_009 reports other buses. A signal combined with a delayed copy of itself, as in an
edge detector, is one signal.

Data that crosses through a memory, as in an asynchronous FIFO, is not a crossing: the FIFO is safe when its pointers
cross safely, which the analysis checks.

**Resets.** The asynchronous reset of each register is traced back to its source. A reset synchronizer is a chain of
two or more registers that the reset clears and that load a constant, such as a shift register of ones; its registers
may take the reset from anywhere. Every other register must be reset by a reset synchronizer of its own clock domain.
A reset input that resets registers directly is released asynchronously (design_015), a reset synchronized to another
clock is too (design_015), and a reset made by logic or by another register is internally generated (design_014).

**Constraints.** Clocks and inputs are described in the **cdc** part of the design section:

.. code-block:: yaml

   design:
     top: board_top
     libraries: ...
     cdc:
       clocks:
         # Names for clock sources: an input port, or the output of a black box
         sys_clk: u_pll.clk_out1
       clock_groups:
         # Synchronous clocks, such as outputs of one PLL with an integer ratio
         - [sys_clk, clk_i]
       inputs:
         # The clock domain of input ports, or async; other inputs are not checked
         uart_rx: async
         sync_rst: sys_clk
       waivers:
         - signal: u_status.flags_meta
           justification: Quasi-static status bits, read only after the run has stopped

A waiver names the destination register of a crossing, as the report names it, or a pattern such as ``u_status.*``.
A waiver without a justification is reported by design_008.

**Report.** :code:`--cdc_report FILE` writes every clock and crossing, with its status, sources and location, and
the reset findings: as JSON for a file ending in .json, otherwise as text:

.. code-block:: text

   $ mhsg --design -c design.yaml --cdc_report cdc.txt
   $ cat cdc.txt
   Clock domain crossing report for olo_base_fifo_async

   Clocks
     In_Clk: port In_Clk, group In_Clk, 10 registers
     Out_Clk: port Out_Clk, group Out_Clk, 11 registers

   Crossings
     i_cc_rd_wr.reg0 (In_Clk) <- i_cc_rd_wr.regin (Out_Clk)
       gray-coded bus: 6 bits of i_cc_rd_wr.regin, gray coded
       at src/base/vhdl/olo_base_cc_bits.vhd:125
     ...

**Rule set.** The **cdc** rule set labels these checks CDC-001 to CDC-009; **do254** maps them to CDC1, SS8 to SS12
and SS15:

.. code-block:: bash

   mhsg --design --lint --rule_set cdc -c design.yaml

.. include:: cdc_coverage.rst

Limitations
-----------

* Only the synthesizable part of the design is analyzed. Testbenches are not supported.
* The design is elaborated with one set of generics. Analyze each configuration that matters, with a configuration file each.
* Vendor primitives must be given as VHDL sources or component declarations which GHDL can elaborate as black boxes.
  A black box is assumed to register its outputs and to use all of its inputs.
* GHDL simplifies the logic while it builds the netlist: it removes registers nothing reads, which design_006 finds by
  comparing the netlist with the clocked processes, and it removes inverter and buffer chains and unused combinational
  signals, which a netlist cannot show. Checks for those are planned for the per-file lint.
* Findings depend on the generics: logic that a generic disables may be constant or unused. Each finding names the
  entity with its generics, as GHDL names it, such as :code:`neorv32_cpu_regfile_5_3`.
* Reconvergence is checked through logic up to the first register in the destination domain, not across further
  registers. Reset domain crossings through logic are not checked yet.
* A black box is assumed to have no path from its inputs to its outputs, so a crossing through one is not found;
  name its clock outputs under clocks.
* Formal reachability is planned.
