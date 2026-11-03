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
     generics:
       DEPTH: 16
     ghdl_options: [-frelaxed-rules]

* **top** is the top entity, and **architecture** optionally its architecture.
* **standard** is the VHDL standard, one of 87, 93, 93c, 00, 02, 08 (the default) or 19.
* **libraries** lists the libraries in the order they are analyzed, each with a **name** and its files.
  **files** lists files and glob patterns; the files of a pattern are sorted, and the order of the list is kept.
  **files_from** names a file which lists one file per line. Lines starting with # or // are comments,
  environment variables are expanded, and relative paths are relative to the list file.
* **top_library** is the library of the top entity, by default the last library.
* **generics** sets generics of the top entity.
* **ghdl_options** are passed to GHDL, for example :code:`-fsynopsys` for designs which use the Synopsys packages.

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

* :code:`design_001` reports the errors of GHDL, such as wrong types and names that are not declared (DO-254 CP1, CP13).
* :code:`design_002` reports latches in the synthesized design (DO-254 SS4).

See :doc:`design_rules`. Design rules are configured like other rules, for example with a different severity.

Limitations
-----------

* Only the synthesizable part of the design is analyzed. Testbenches are not supported.
* The design is elaborated with one set of generics. Analyze each configuration that matters, with a configuration file each.
* Vendor primitives must be given as VHDL sources or component declarations which GHDL can elaborate as black boxes.
* Clock domain crossing analysis and the other design checks of the DO-254 rule set are planned.
