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

MHSG loads the plugin with :code:`yosys -m ghdl`, unless the ghdl command is built into Yosys, as in the MSYS2
packages for Windows, which have no plugin to load. MHSG asks Yosys once which it is.

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
* **libraries** lists the libraries in the order they are analyzed, each with a **name** and its files, unless
  **order** is **auto**.
  **files** lists files and glob patterns; the files of a pattern are sorted, and the order of the list is kept.
  **files_from** names a file which lists one file per line. Lines starting with # or // are comments,
  environment variables are expanded, and relative paths are relative to the list file.
  **exclude** lists patterns of files to leave out, such as testbenches or files of a missing submodule.
* **top_library** is the library of the top entity, by default the last library.
* **order** set to **auto** lets GHDL find the order the files are analyzed in, for designs whose files are not
  listed in compile order, such as a whole source directory given by a glob pattern. GHDL reads every VHDL file of the
  libraries (:code:`ghdl -i`) and gives the order the top entity needs (:code:`--elab-order`); files the top does not
  use are not analyzed. The default, **listed**, analyzes the libraries and their files in the order given.
* **generics** sets generics of the top entity: numbers, booleans, strings, vectors as bits, such as ``"00000111"``,
  single bits and characters, such as ``1`` for a std_logic, and times, such as ``10 ns``.
  Every generic without a default value must be set, and every generic set must exist; otherwise design_001 reports
  it before GHDL runs, since GHDL would quietly use the leftmost value of the type, such as 1 for a positive.
  GHDL cannot set a generic of type real or time from the command line, so MHSG analyzes a copy of the file of the top
  entity in which the value is the default. Findings still name the original file, at the same lines.
* **ghdl_options** are passed to GHDL, for example :code:`-fsynopsys` for designs which use the Synopsys packages.
* **work_directory** keeps the files of GHDL and Yosys, such as the Verilog and the JSON netlist, in a directory,
  for a closer look. Without it they are written to a temporary directory and removed.

What design analysis needs from the VHDL files themselves, such as the processes and their assignments, is kept in a
cache, so a file is only parsed again when it changes: in :code:`$MHSG_CACHE_DIRECTORY`, else
:code:`$XDG_CACHE_HOME/mhsg`, else :code:`~/.cache/mhsg`. :code:`MHSG_CACHE_DIRECTORY` set to nothing turns it off.

Paths in the configuration may use environment variables.

Verilog, SystemVerilog and mixed designs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The files of a design may be Verilog and SystemVerilog, by their extensions :code:`.v`, :code:`.vh`, :code:`.sv`
and :code:`.svh`, alone or with VHDL files:

.. code-block:: yaml

   design:
     top: fifo
     libraries:
       - name: work
         files: [rtl/fifo_pkg.sv, rtl/fifo.sv]
     defines:
       SYNTHESIS:
       DEPTH: 16
     include_directories: [rtl/include]
     generics:
       Width: 8

* **defines** are the macros of the command line, :code:`-D` for the tools; a macro with no value is just defined.
* **include_directories** are searched by :code:`\`include`.
* **generics** set the parameters of a Verilog top module.

A design of Verilog and SystemVerilog only needs Yosys, not GHDL. Yosys reads the files with the read_slang command of
the `yosys-slang <https://github.com/povik/yosys-slang>`_ plugin when it has it, as in the YosysHQ OSS CAD Suite;
without it, with its own reader, :code:`read_verilog -sv`, which reads Verilog and part of SystemVerilog: designs that
use packages with typed parameters, casts or interfaces need the plugin. Yosys puts the source location on every
cell, and a finding is moved to the line of the assignment, as for VHDL.

In a mixed design with a VHDL top, GHDL elaborates the VHDL as for a VHDL design and leaves the instances of
components without a VHDL entity unbound; Yosys reads the Verilog files and links those instances to the Verilog
modules of the same name, so the analysis sees through them.

In a mixed design with a Verilog top, GHDL analyzes the VHDL files and Yosys elaborates each VHDL entity the Verilog
instantiates with the ghdl command, before it reads the Verilog and elaborates the top module with its parameters set
under **generics**. With :code:`order: auto`, the VHDL files are those these entities need. Limits:

* an instance that sets parameters gets the entity elaborated with those values, once for each set of values, by
  name or by position, also in a generate block. pyslang elaborates the Verilog from the top first, with a stand-in
  module for each entity, to compute the values: literals, such as :code:`8`, :code:`16'd16` or :code:`"FAST"`, and
  expressions of parameters, also of the module that holds the instance. Yosys then reads a copy of each file with
  such instances, in which each names the module elaborated with its values; findings and messages name the original
  file. An instance whose values differ between the times the elaboration meets it, as in a generate loop that gives
  each iteration other values, or in a module elaborated with several sets of parameters, is reported by design_001
  and analyzed with the defaults of the generics; so is one whose values cannot be computed, and a string generic
  set from an expression;
* GHDL names the module after the entity in lower case; the Verilog may write the name in any case, as long as all its
  instances write it the same way;
* with read_slang, this has not been tried yet.

A module the Verilog files instantiate but none defines, such as a vendor primitive or encrypted IP, is a black box, as
a VHDL component without an entity is (see `Black boxes`_). Yosys reads a module without logic for it before the
design, so its hierarchy check does not stop there, with the ports the instances connect:

* when the design names a black box library Yosys has cell models for, such as :code:`black_box_libraries: [xilinx]`,
  the primitives come from those models, with their ports: :code:`+/xilinx/cells_sim.v` and :code:`cells_xtra.v` for
  xilinx, :code:`+/ecp5/cells_sim.v`, :code:`cells_bb.v` and :code:`+/ice40/cells_sim.v` for lattice, and
  :code:`+/sf2/cells_sim.v` for the SmartFusion2 macros of microchip;
* otherwise a port's direction comes from its role in the declaration: a clock, an enable, a reset input or a static
  port is an input, a path, a clock output, a reset output or a synchronized output is an output, and so is each port
  another role names as its input;
* a port whose role does not say, such as :code:`async` or :code:`{sync: aclk}`, is an input of an instance when
  something else drives what it connects to, and an output when nothing does.

The modules are written to :code:`black_boxes.v` in the work directory. design_017 reports a black box without a
declaration. With read_slang, this has not been tried yet.

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
2. GHDL synthesizes the top entity to Verilog, which is only read for the source locations GHDL writes in it:
   comments such as :code:`/* fifo.vhd:42:5 */`, or Yosys src attributes such as :code:`(* src="fifo.vhd:42.5" *)`
   in later versions of GHDL. Builds of GHDL that write neither give findings without a location.
3. Yosys synthesizes the same top entity through the GHDL plugin and writes the netlist before any optimization.
4. The design rules check the result. Each cell of the netlist is located in the VHDL by joining its name to the
   location in GHDL's Verilog, and a latch is reported at the assignment that infers it.

For a Verilog and SystemVerilog design, Yosys reads the files, elaborates the top module and writes the netlist; the
cells carry their source locations as src attributes.

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
* :code:`design_019`, disabled by default as it takes longer, maps the design to look-up tables of :code:`lut_size`
  inputs and reports each register and output port reached by a path of more than :code:`maximum_levels` levels, 8
  by default, with the register or port the path starts at.

* :code:`design_008` to :code:`design_016` check clock domain crossings, clocks and resets, see below.
* :code:`design_017` reports black boxes whose clock domain behaviour is not declared, see below.
* :code:`design_018` reports reset domain crossings: data from a register with one asynchronous reset into a register
  of the same clock that another asynchronous reset clears, unless that reset also comes from the first.
* :code:`design_020` reports memory outputs that decide an if condition or a case selector (STARC 2.10.1.7, 2.10.1.8).
* :code:`design_021` reports buses with more than :code:`maximum_drivers` tri-state drivers, 5 by default, counted
  across the hierarchy (STARC 2.5.1.4).
* :code:`design_022` reports resets used both as an asynchronous and as a synchronous reset (STARC 1.3.1.6).
* :code:`design_023` reports inout ports wired directly to an input or output port of the same module (STARC 2.5.1.6).
* :code:`design_024`, disabled by default as it takes longer, maps the design to gates and reports modules whose own
  logic has more than :code:`maximum_gates` NAND gate equivalents, 40000 by default (STARC 1.6.1.1).

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
|                                | next. The registers may be the bits of one vector, shifted along it.            |
+--------------------------------+---------------------------------------------------------------------------------+
| gray-coded bus                 | The bits of a bus synchronized one by one, loaded with the gray code of a       |
|                                | value, or a choice between such codes, so only one bit changes at a time.       |
+--------------------------------+---------------------------------------------------------------------------------+
| qualified by enable            | Data held stable and captured when an enable synchronized to the destination    |
|                                | clock allows it, as in a handshake.                                             |
+--------------------------------+---------------------------------------------------------------------------------+
| bus synchronized bit by bit    | Several bits of one register synchronized one by one, by one register or by     |
|                                | registers of a bit each: they can arrive in different cycles. A bit synchronized|
|                                | alone beside them, such as a flag of the same record, is a signal of its own.   |
|                                | Reported by design_009.                                                         |
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
destination clock, and two synchronizers of the same signal can disagree for a cycle. Logic that combines them can see
a state the source never had. Every synchronizer tags its output, and the tags follow the signal forward through logic,
registers, memories and feedback loops such as state machines in the destination domain. Where tags of two
synchronizers from the same source domain first meet, at a register, a memory, a black box input or an output,
design_016 reports a reconvergence; registers further on are not reported again. The search is structural, so it finds
every meeting, whether or not a test exercises it.

* The bits of one bus share a tag: a gray-coded bus is meant to be combined, and design_009 reports other buses.
* A signal combined with a delayed copy of itself, as in an edge detector, carries one tag.
* A synchronous reset, an input that loads a constant into two or more registers, is a reset path rather than data
  and is not followed, unless design_016 has :code:`follow_resets: true`. A set or clear of a single register is
  followed. The crossing report lists the meetings through resets either way.

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
       clears:
         # Synchronous clears computed by logic, followed like data by design_016
         - u_ctrl.clear_r

A waiver names the destination register of a crossing, as the report names it, or a pattern such as ``u_status.*``.
**clears** names registers, or patterns, that load a constant into other registers as a clear rather than a reset.
design_016 does not follow a synchronous reset of two or more registers, unless :code:`follow_resets` is set; a clear
it lists is followed like data. Structure cannot tell the two apart: reset crossing circuits compute their resets
with logic too.
A waiver without a justification is reported by design_008. Other findings of design analysis are waived with the
waivers of the configuration, see :ref:`waivers`.

**Report.** :code:`--cdc_report FILE` writes every clock and crossing, with its status, sources and location, and
the reset findings: as JSON for a file ending in .json, otherwise as text. It ends with the record of the run, the
versions of MHSG, GHDL and Yosys and the configuration used (see :ref:`the record of the run <run_record>`):

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

   Run
     Tools: mhsg 3.36.0, Python 3.12.3, pyslang 12.1.0, GHDL 4.1.0 (Ubuntu 4.1.0+dfsg-0ubuntu2) [Dunoon edition], Yosys 0.33 (git sha1 2584903a060)
     Configuration: design.yaml (sha256 9c41e7...)
     Command line: --design -c design.yaml --cdc_report cdc.txt

**Rule set.** The **cdc** rule set labels these checks CDC-001 to CDC-009; **do254** maps them to CDC1, SS8 to SS12
and SS15:

.. code-block:: bash

   mhsg --design --lint --rule_set cdc -c design.yaml

.. include:: cdc_coverage.rst

Black boxes
-----------

A black box is an instance whose logic design analysis cannot see: a vendor primitive such as a clock buffer or a
PLL, a vendor macro, encrypted IP, or any component without an entity. Nothing is assumed about a black box. Every
black box type must be declared, whatever its vendor, with a role for every port; design_017 reports a black box that
is not declared, a port without a role, and a static port without a justification and a reviewer. Until then, the
crossings through it are not known.

**Vendor libraries.** A design that uses vendor primitives through a library, such as
``library unisim; use unisim.vcomponents.all;``, needs the vendor's component declarations to analyze.
MHSG reads them from your own installation of the vendor tools, listed under **vendor_libraries**, and analyzes them
before the libraries of the design. Nothing from the vendors is copied into MHSG.

.. code-block:: yaml

   design:
     top: board_top
     vendor_libraries:
       - xilinx                              # unisim and xpm
       - vendor: microchip
         family: polarfire
         path: /opt/microchip/Libero_SoC_v2024.1
       - library: unimacro                   # any library, from listed files
         files: [/opt/xilinx/unimacro_VCOMP.vhd]
     libraries: ...

+---------------+-------------------------------+--------------------------------------------------------+-----------------------------------------+
| Vendor        | Installation from             | Files, relative to the installation                    | Libraries                               |
+===============+===============================+========================================================+=========================================+
| ``xilinx``    | path, $XILINX_VIVADO,         | data/vhdl/src/unisims/unisim_VPKG.vhd (if present),    | unisim, xpm (if present)                |
|               | $XILINX_VIVADO_HOME           | data/vhdl/src/unisims/unisim_VCOMP.vhd,                |                                         |
|               |                               | data/ip/xpm/xpm_VCOMP.vhd                              |                                         |
+---------------+-------------------------------+--------------------------------------------------------+-----------------------------------------+
| ``microchip`` | path, $LIBERO_INSTALL_DIR,    | Designer/lib/vhdl/<family>.vhd, or                     | <family>, such as polarfire             |
|               | $LIBERO_ROOT,                 | SynplifyPro/lib/microsemi/<family>.vhd, or             |                                         |
|               | $SYNPLIFY_PRO_ROOT            | lib/microsemi/<family>.vhd, or the same under actel    |                                         |
+---------------+-------------------------------+--------------------------------------------------------+-----------------------------------------+
| ``intel``     | path, $QUARTUS_ROOTDIR,       | eda/sim_lib/altera_mf_components.vhd,                  | altera_mf, altera, lpm, and <family>    |
|               | $QUARTUS_ROOT                 | altera_primitives_components.vhd, 220pack.vhd and      | if given                                |
|               |                               | <family>_components.vhd (if present)                   |                                         |
+---------------+-------------------------------+--------------------------------------------------------+-----------------------------------------+
| ``lattice``   | path, $RADIANT_HOME,          | cae_library/synthesis/vhdl/<family>.vhd                | <family>, such as ecp5u                 |
|               | $LSC_RADIANT, $LSC_DIAMOND,   |                                                        |                                         |
|               | $DIAMOND_HOME, $FOUNDRY       |                                                        |                                         |
+---------------+-------------------------------+--------------------------------------------------------+-----------------------------------------+

These locations can differ between versions of the tools. When a file is not found, MHSG lists every location it
tried; set **path** to the installation, or name the files with **library** and **files**. Only declaration files
belong here: a library of simulation models would make GHDL synthesize the models instead of keeping black boxes.
The vendor files are analyzed with the standard and **ghdl_options** of the design.

**Without a vendor installation**, :code:`stubs: true` makes MHSG write the packages the design uses from a vendor
library, such as :code:`unisim.vcomponents`, into :code:`stubs` in the work directory, with a component declaration for
each vendor component the design instantiates:

.. code-block:: yaml

   vendor_libraries:
     - vendor: xilinx                        # stub packages of unisim and xpm
       stubs: true
     - library: vendorlib                    # of any library
       stubs: true

A stub declares only the ports and generics the instances name, so the instances must associate by name:

* the type of a port is that of its actual: the declared type of the signal, port or record element, its element
  type for an indexed name, std_logic for a character literal, std_logic_vector for a string, bit string or
  aggregate. Subtypes of the design, such as :code:`subtype sl is std_logic`, resolve to their base types. An array
  port takes the width its instances agree on, from the declared range, a slice or a literal; ranges may use
  constants and generics with integer values. An aggregate or an open port whose width no instance gives gets one
  element, which is enough for analysis;
* the mode of a port comes from Yosys' cell model of the primitive, when the design names a black box library Yosys
  has models for, such as :code:`black_box_libraries: [xilinx]`; then from the black box declaration where a role
  says it, such as :code:`clock` or :code:`path`. Otherwise a port whose actual is an input of the entity, a signal the
  design assigns, a literal or an expression is an input; any other port is an output, unless another output already
  drives its signal;
* the type of a generic is that of its actual: integer, real, boolean, string, time, bit_vector for a bit string,
  the return type of a function, or the declared type of a constant or generic. A generic that some instances leave
  out gets the first literal value.

The types a stub can declare are those of the packages std.standard, ieee.std_logic_1164 and ieee.numeric_std. An
actual of another type, such as an enumeration of the design, is declared as std_logic, with a comment naming the
type in the stub; GHDL reports the mismatch if the instance is analyzed. A file that uses two stub libraries, such as
unisim and xpm, takes the components whose names start with :code:`xpm_` from xpm. A stub says nothing about the
primitive beyond what the design shows, which is all design analysis needs of a black box: the vendor's own files
remain the reference, and a mistake in an instance that the vendor's declarations would catch, such as a misspelled
port, goes unnoticed with stubs. The real-world check analyzes the hard FIFO of hdl-modules and the clock manager of
surf this way.

Each vendor primitive is then a black box, to be declared as below.

Write the declarations in the **black_boxes** part of the design section, keyed by component name or a pattern, or in
library files shared between designs:

.. code-block:: yaml

   design:
     top: board_top
     libraries: ...
     black_box_libraries: [../common/xilinx_black_boxes.yaml]
     black_boxes:
       BUFGCE:
         archetype: clock_buffer
         input: I
         output: O
         enable: CE
         reference: UG953, BUFGCE
       xpm_cdc_single:
         archetype: synchronizer
         source_clock: src_clk
         destination_clock: dest_clk
         input: src_in
         output: dest_out
         stages: DEST_SYNC_FF
       vendor_dma:
         reference: DMA product guide, section 3
         reviewed_by: H. Reid
         ports:
           aclk: clock
           s_axi_*: {sync: aclk}
           irq: async
           cfg_mode: {static: Written once at boot, before aclk starts}
     black_box_instances:
       u_top.u_dma_test:
         ports:
           irq: unused

A library file has the same **black_boxes** and **black_box_instances** keys. The design section takes precedence over
libraries, and a declaration of an instance, by path or pattern, over the declaration of its type.

**Roles.** A port role is one of:

+---------------------------------------------------+------------------------------------------------------------------+
| Role                                              | Meaning                                                          |
+===================================================+==================================================================+
| ``clock``                                         | A clock input.                                                   |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{sync: <clock pin>}``                           | Data timed by a clock pin of the black box. Data from another    |
|                                                   | clock domain into such an input is a crossing. The inputs timed  |
|                                                   | by one pin are taken together: separately synchronized signals   |
|                                                   | that enter two of them meet in the box (design_016).             |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{path: [<inputs>]}``                            | An output that follows inputs without a register, such as an     |
|                                                   | input buffer. Clocks and data are followed through it.           |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{clock_out: {from: <pin>, relation: <r>}}``     | A clock output: ``same`` for a buffer, ``derived`` for a clock   |
|                                                   | synchronous to its input, such as a PLL output, ``independent``  |
|                                                   | for a new asynchronous clock, such as a recovered clock.         |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{enable: <clock output>}``                      | The enable of a clock buffer.                                    |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{reset_in: async}``, ``{reset_in: {sync: <c>}}``| A reset input.                                                   |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{reset_out: {clock: <pin>, release: <r>}}``     | A reset output released ``sync`` or ``async`` to a clock pin.    |
+---------------------------------------------------+------------------------------------------------------------------+
| ``async``                                         | An output that changes asynchronously, such as an interrupt or   |
|                                                   | a lock signal, or an input sampled asynchronously.               |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{synchronized: {clock, from, stages}}``         | An output synchronized inside the black box, such as a vendor    |
|                                                   | synchronizer macro. Listed in the crossing report for manual     |
|                                                   | review, with its stages, a number or the name of a generic, and  |
|                                                   | tagged as a synchronizer for reconvergence.                      |
+---------------------------------------------------+------------------------------------------------------------------+
| ``{static: <justification>}``                     | Configuration that only changes while the design is idle; left   |
|                                                   | out of the crossing checks. Needs **reviewed_by**, on the port   |
|                                                   | as ``{static: {justification, reviewed_by}}`` or on the          |
|                                                   | declaration.                                                     |
+---------------------------------------------------+------------------------------------------------------------------+
| ``unused``                                        | A port with no effect on clock domains.                          |
+---------------------------------------------------+------------------------------------------------------------------+

A port that another role names, such as the input of a path, needs no role of its own. Port names and patterns, such
as ``s_axi_*``, match in any case. **reference** and **reviewed_by** are printed in the crossing report.

**Archetypes.** An archetype writes the roles of a common kind of black box from a few names; **ports** can add to or
override them:

+------------------------+---------------------------------------------------+------------------------------------------+
| Archetype              | Parameters                                        | Roles                                    |
+========================+===================================================+==========================================+
| ``buffer``             | input, output                                     | output follows input                     |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``clock_buffer``       | input, output, enable                             | the same clock, with an enable           |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``clock_generator``    | input, outputs, relation (derived), reset, locked | derived clocks, asynchronous lock output |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``single_clock``       | clock, async_reset                                | every other port timed by the clock      |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``dual_clock``,        | sides: {clock pin: [ports]}                       | ports timed by their clock; a FIFO is    |
| ``memory``,            |                                                   | listed for manual review                 |
| ``dual_clock_fifo``    |                                                   |                                          |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``synchronizer``       | source_clock, destination_clock, input, output,   | a synchronized output                    |
|                        | stages                                            |                                          |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``async_input``        | outputs (all)                                     | asynchronous outputs                     |
+------------------------+---------------------------------------------------+------------------------------------------+
| ``static``             | justification, reviewed_by                        | every port static                        |
+------------------------+---------------------------------------------------+------------------------------------------+

**Variants.** Roles that depend on generics, whose values GHDL keeps, go under **variants**:

.. code-block:: yaml

   fifo_generator_0:
     archetype: dual_clock_fifo
     sides: {wr_clk: [din, wr_en, full], rd_clk: [dout, rd_en, empty]}
     variants:
       - when: {COMMON_CLOCK: 1}
         ports: {dout: {sync: wr_clk}, rd_en: {sync: wr_clk}, empty: {sync: wr_clk}}

**Template.** :code:`mhsg --design -c design.yaml --black_box_template black_boxes.yaml` writes a declaration for each
black box type that has none, with its instances, generic values, ports, directions and widths, and every role
``TODO``. Fill it in, then add it to **black_box_libraries** or copy it into the design section; design_017 reports
every ``TODO`` that remains.

**Libraries that come with MHSG.** Four declaration libraries come with MHSG, for AMD/Xilinx, Microchip, Intel and
Lattice. A design includes them by name, so using them stays your decision:

.. code-block:: yaml

   design:
     vendor_libraries: [xilinx]
     black_box_libraries: [xilinx]
     black_boxes:
       # Changes a single port of a declaration of the library
       BUFGMUX:
         ports: {O: {clock_out: {from: I0, relation: same}}}

The declarations are taken from the vendors' published libraries guides, not from vendor files. A declaration in the
design section, or a library listed earlier, takes precedence port by port, so a single port can be changed. Ports
whose behaviour depends on how a primitive is used, such as the cascade ports of the SERDES or the latch mode of the
Microchip SLE, are left out on purpose, so design_017 asks for them. Check the declarations against the guides of your
tool versions. The port names of the primitives Yosys has cell models for were checked against those models.

* **xilinx**: clock buffers, input and output buffers, MMCM and PLL, registers, shift registers, DSP, IDDR and ODDR,
  IDELAY and ODELAY, ISERDES and OSERDES, block RAM with its ECC and cascade ports, configuration primitives, and the
  XPM CDC macros, FIFOs and memories, the transceivers of the 7 series, UltraScale and UltraScale+ families and the
  PCI Express blocks. The output of a clock multiplexer is a clock of its own; MMCM and PLL outputs are derived from
  CLKIN1; the clock outputs of a transceiver are clocks of their own, and its TX and RX ports are timed by TXUSRCLK2
  and RXUSRCLK2. The user side of the UltraScale+ PCI Express blocks, which have two user clocks, and the PCI Express
  ports of the UltraScale transceivers are left for the design to declare.
* **microchip**: global and regional clock buffers, input and output buffers, SLE, the large SRAM blocks, micro SRAM,
  the math block, and the PF_CCC, PF_OSC, PF_INIT_MONITOR and CoreReset_PF cores, matched by the names Libero gives
  them, such as PF_CCC_C0.
* **intel**: the GLOBAL buffer, altpll, altsyncram, dcfifo, scfifo, altddio_in and altddio_out. The side B ports of
  altsyncram follow the clock its ADDRESS_REG_B and OUTDATA_REG_B parameters select.
* **lattice**: for ECP5, the DCCA and DCSC clock primitives, EHXPLLL, OSCG, IB, OB, OBZ and BB buffers, IDDRX1F and
  ODDRX1F, the FD1S3 and FD1P3 registers, DP16KD and PDPW16KD block RAM and GSR; for iCE40, SB_GB, SB_GB_IO, the
  SB_PLL40 PLLs, the oscillators, SB_RAM40_4K and the SB_DFF registers.

xilinx
~~~~~~

.. include:: black_box_library_xilinx.rst

microchip
~~~~~~~~~

.. include:: black_box_library_microchip.rst

intel
~~~~~

.. include:: black_box_library_intel.rst

lattice
~~~~~~~

.. include:: black_box_library_lattice.rst

**Report.** The crossing report lists each black box type, where it is declared, its reference and reviewer, the
outputs synchronized inside black boxes for manual review, the static ports with their justification and reviewer,
and the problems of the declarations.

Limitations
-----------

* Only the synthesizable part of the design is analyzed. Testbenches are not supported.
* The design is elaborated with one set of generics. Analyze each configuration that matters, with a configuration file each.
* Vendor primitives must be given as VHDL sources or component declarations which GHDL can elaborate as black boxes.
  The netlist checks, design_002 to design_007, take a black box output to be registered unless the declaration of
  the black box type gives it a :code:`path` role: design_003 then finds loops through it and design_007 follows paths
  through it, without counting a logic level for the box. When declarations of single instances differ between the
  instances of a module, design_003 and design_007 check a copy of the module for each instance, so each declaration
  applies to its instance; the other netlist checks see the declaration of the black box type. Every input of a black
  box counts as used, whatever its role.
* GHDL simplifies the logic while it builds the netlist: it removes registers nothing reads, which design_006 finds by
  comparing the netlist with the clocked processes, and it removes inverter and buffer chains and unused combinational
  signals, which a netlist cannot show. Checks for those are planned for the per-file lint.
* Findings depend on the generics: logic that a generic disables may be constant or unused. Each finding names the
  entity with its generics, as GHDL names it, such as :code:`neorv32_cpu_regfile_5_3`.
* What a black box does with its inputs is known only from its declaration: reconvergence follows its paths and
  takes the inputs timed by one clock pin together; other inputs count one bit at a time.
* Formal reachability is planned.
