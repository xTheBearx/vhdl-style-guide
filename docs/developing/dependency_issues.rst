.. _dependency_issues:

Problems Found in Dependencies
==============================

The tools and libraries MHSG uses have bugs, limitations and surprising behaviour that shaped how MHSG uses them. Each
entry says what happens, how to see it, and what MHSG does about it, so a workaround is not removed by mistake and can
be dropped once the tool is fixed. None has been reported upstream yet.

Keep this page up to date: add an entry when a workaround for a tool is written, and say when a newer version fixes
it.

* **Bug**: the tool contradicts its documentation or the language standard.
* **Limitation**: a feature the tool does not have, documented or not.
* **Quirk**: surprising behaviour that is arguably by design.

The versions are those the problems were found with: GHDL 4.1.0 (Ubuntu 4.1.0+dfsg-0ubuntu2.1, mcode backend),
Yosys 0.33 (git sha1 2584903a060), yosys-plugin-ghdl 0.0~git20230419.5b64ccf-1ubuntu2, Verilator 5.020 (Debian
5.020-1), pyslang 12.1.0 and Sphinx 9.1.1.

GHDL
----

**Bug: --elab-order lists nothing for files imported by an absolute path.** :code:`ghdl --elab-order` exits with 0 and
prints nothing when the files were imported with :code:`ghdl -i` by absolute paths; imported by relative paths, the same
files are listed in order:

.. code-block:: bash

   ghdl -i --std=08 --workdir=order --work=util /abs/order_pkg.vhd
   ghdl -i --std=08 --workdir=order --work=work /abs/order_top.vhd /abs/order_leaf.vhd
   ghdl --elab-order --std=08 --workdir=order -Porder --work=work order_top   # prints nothing

MHSG imports by paths relative to the current directory (:code:`mhsg/design/runner.py`, :code:`order: auto`).

**Bug: a generic of the top without a default is elaborated with the first value of its type.** A top-level generic
such as :code:`Width_g : positive` with no default and no :code:`-g` value is elaborated as 1 without a message, while
an unconstrained :code:`std_logic_vector` generic gives the error :code:`generic "Polynomial_g" has no default value`.
design_001 reports every generic without a default that the design section does not set, before GHDL runs
(:code:`mhsg/design/top.py`).

**Bug: ghdl synth --out=verilog writes a latch without its enable.** For
:code:`if en = '1' then q <= d; end if;` in a process, :code:`ghdl synth --latches --out=verilog` writes
:code:`always @(en) n5_q <= d;`, which Yosys reads as combinational logic. MHSG reads the netlist of the GHDL plugin
and uses GHDL's Verilog only for the source locations in its comments (:code:`mhsg/design/netlist.py`).

**Limitation: -g cannot set a generic of type real.** :code:`ghdl synth -gClkFreq_g=100000000 olo_intf_uart` stops with
:code:`unhandled override for generic "ClkFreq_g"`. A vector value must be given without quotes:
:code:`-gX="1100000"` gives :code:`incorrect character '"' in string`. MHSG analyzes a copy of the file of the top in
which the default is the value (:code:`patch_real_generics` in :code:`mhsg/design/top.py`).

**Limitation: a RAM written from two processes through a shared variable does not synthesize.** Open Logic's
olo_base_ram_tdp stops with :code:`multiple assignments for "Mem_v" offsets 0:0`. No workaround; listed in the
:doc:`backlog`.

**Limitation: synthesis removes logic, even with the keep attribute.** Inverter chains, registers nothing reads and
signals nothing assigns are folded or removed before Yosys sees the netlist; a keep attribute stays on the net but the
logic is folded all the same. Delay chains (DO-254 SS1) are left to per-file checks, and design_006 finds unused
registers in the source.

**Limitation: two instances driving one signal are not reported.** :code:`ghdl synth` succeeds; design_004 finds the
drivers in the netlist, and Yosys' :code:`check` reports :code:`multiple conflicting drivers`.

**Limitation: ghdl synth checks the widths of a branch a constant condition never selects.** In
:code:`y <= a when WIDE_G else (others => b);` with :code:`WIDE_G` false and :code:`a` wider than :code:`y`, simulation
runs, the analysis only warns, and :code:`ghdl synth` stops with :code:`out of bound expression` (through the Yosys
plugin: :code:`mismatching vector length`). surf's SimpleDualPortRam assigns its write enables this way, so the surf
designs that use it, such as AxiLiteAsync, cannot be analyzed; design_001 reports the error.

**Quirk: an assert in a clocked process becomes a register.** The register holds the condition until the clock edge and
feeds only a :code:`$assert` cell. design_005 reported a constant one as never changing; the register graph now leaves
out registers that only feed assertions (:code:`assertion_register` in :code:`mhsg/design/graph.py`).

**Quirk: synthesis stops at the first latch.** Without :code:`--latches`, the first latch is an error. With it, a latch
written with a case statement and :code:`null` becomes a multiplexer looped on itself rather than a :code:`$dlatch`
cell. MHSG passes :code:`--latches` and finds the looped multiplexers too (:code:`Netlist.latches` in
:code:`mhsg/design/netlist.py`).

**Quirk:** :code:`ghdl synth --help` fails with :code:`unknown command option`; the help is :code:`ghdl help synth`.

GHDL plugin for Yosys
---------------------

**Bug (Ubuntu package): the plugin does not find the std library.** Yosys stops with
:code:`warning: ieee library directory '/usr/lib/ghdl/gcc/vhdl/ieee/v08/' not found` and
:code:`error: cannot find "std" library`, as the plugin looks for the gcc backend while only mcode is installed. MHSG
sets :code:`GHDL_PREFIX` to the library prefix that :code:`ghdl --disp-config` gives (:code:`mhsg/design/tools.py`).

**Limitation: the netlist has no source locations.** The plugin writes no :code:`src` attributes, in the Ubuntu package
and at upstream commit c21051d. MHSG matches cells by GHDL's instance numbers to the :code:`/* file:line:col */`
comments of the Verilog that :code:`ghdl synth --out=verilog` writes (:code:`mhsg/design/netlist.py`). Newer builds,
such as the OSS CAD Suite's, do write them, and MHSG reads them when present.

**Quirk: errors of GHDL go to standard error; Yosys' log only says** :code:`ERROR: vhdl import failed.` The runner
reads standard error for the messages.

**Limitation: an inout port the entity does not drive reads as** :code:`'z'`. In the netlist of the plugin,
:code:`pout <= pin` of an inout port :code:`pin` becomes a constant :code:`z` on both ports, where
:code:`ghdl synth --out=verilog` keeps :code:`assign pout = pin`. design_023 therefore finds inout ports wired to
other ports in Verilog modules only; in VHDL the modes of ports forbid most such connections anyway.

**Limitation: two tri-state drivers in one architecture are an error.** GHDL stops with
:code:`multiple assignments for "bus" offsets 0:0` (design_001) for two concurrent assignments of :code:`'Z'` to one
resolved signal; tri-state drivers in separate instances are accepted, and design_021 counts those.

Yosys
-----

**Limitation: read_verilog -sv does not read much SystemVerilog.** It stops on Ibex' casts
(:code:`rtl/ibex_pkg.sv:322: ERROR: syntax error, unexpected OP_CAST`) and on common_cells' typed parameters
(:code:`unexpected TOK_ID, expecting ',' or '=' or ')'`). MHSG uses :code:`read_slang` when Yosys has the yosys-slang
plugin, and :code:`read_verilog -sv` otherwise (:code:`mhsg/design/tools.py`).

**Limitation: yosys-slang is not packaged for Ubuntu.** It needs the YosysHQ OSS CAD Suite or a build from source.

**Quirk: opt removes logic and turns registers that are never enabled into latches.** MHSG writes the netlist before
:code:`opt` runs.

SymbiYosys
----------

**Limitation: SymbiYosys is not packaged for Ubuntu.** design_025 needs the YosysHQ OSS CAD Suite (sby of 2026-11,
with yices and abc pdr), and runs the tools beside :code:`sby`, as it calls :code:`yosys`, :code:`yosys-smtbmc` and the
solvers by name (:code:`mhsg/design/formal.py`).

**Quirk: a cover run stopped by its time limit names no reached branches in its summary.** smtbmc names each cover cell
as it reaches it; MHSG names the cells after the branches and reads those lines too, so the branches reached before
the limit count.

**Quirk: in cover mode, assertions of the design are checked too**, and a failing one ends the run. MHSG leaves the
assertions and covers of the design out of the formal netlist and keeps its assumptions.

Verilator
---------

**Quirk: an include file is not looked for in the directory of the file including it.** Verilator stops with
:code:`Cannot find include file: prim_assert.sv` where slang finds it next to the including file; IEEE 1800 leaves the
search to the tool. MHSG passes the directory of each file of the run as an include directory
(:code:`mhsg/svFile/verilator.py`).

**Quirk: a missing module stops --lint-only.** :code:`Cannot find file containing module` is an error even when only
linting. MHSG writes an empty stub module for each module the run instantiates but does not define, with the ports and
parameters of its instances.

**Quirk: the first error in any file stops the whole run.** MHSG leaves out the files slang cannot parse and those
importing a package the run does not define, and runs Verilator again, up to 10 times, without the files it stopped
at.

**Limitation: some SystemVerilog is rejected as unsupported.** Cycle delay ranges (:code:`##[1:3]`), clocking event
edge overrides and :code:`sequence` declarations give :code:`Unsupported:` errors; those files are left out of
Verilator's run.

Verilator also requires a package to be declared before the files that import it (:code:`PKGNODECL`), as IEEE 1800-2017
26.3 does; MHSG gives it the files defining packages first.

pyslang and slang
-----------------

These are quirks of the API, handled where the syntax tree is read:

* A separated list holds its comma tokens between the items; :code:`elements` in :code:`mhsg/rules/sv_tree.py` leaves
  them out.
* A token that is missing is an empty token of kind :code:`Unknown`, not None; a type that is missing is None.
* An implicit type is a zero-width :code:`Placeholder` token at the offset of the next token
  (:code:`mhsg/svFile/svFile.py`).
* Offsets count bytes of UTF-8, not characters (:code:`mhsg/svFile/svFile.py`, :code:`mhsg/svFile/verilator.py`).
* :code:`SyntaxTree.fromText` makes the declaration itself the root of a tree with one declaration; :code:`nodes` in
  :code:`mhsg/svFile/verilator.py` includes the root.
* :code:`SyntaxTree` is in :code:`pyslang.syntax`, and pylint cannot see the submodules of the extension, hence the
  :code:`import-error` disables.

Sphinx
------

**Not confirmed: an incremental build gave a duplicate label warning that a full build does not.** A strict build of a
copy of the documentation, updated file by file, warned :code:`duplicate label lint, other instance in
systemverilog.rst`; a full build of the same files was clean. The copy kept the files' modification times, so this may
come from the update rather than from Sphinx. CI builds from scratch with :code:`-W --keep-going`.

Python
------

Two workarounds come from VSG: the number of jobs is limited to 60 for the process pool on Windows
(https://bugs.python.org/issue26903, :code:`mhsg/cmd_line_args.py`), and the function the pool runs is in its own module,
as functions of :code:`__main__` cannot be pickled (https://bugs.python.org/issue25053, :code:`mhsg/apply_rules.py`).

Test and lint tools
-------------------

* **pytest-html-reporter** was suspected of intermittent :code:`JSONDecodeError` failures with pytest-xdist (VSG issue
  1157), with workers writing :code:`output.json` at the same time; it was not reproduced, and the plugin was removed.
* **codespell** takes some HDL names, such as the plural of inout, for misspellings; they are listed in
  :code:`.codespell-ignore`.
* **pylint** reports attributes that subclasses or mixins set, and values already checked for None; those lines have
  targeted disables.

Defects found in the test projects
----------------------------------

Design analysis of the real-world designs found these problems in their code, see
:code:`scripts/real_world_designs.yaml`:

* **neorv32** (ca86862), :code:`rtl/core/neorv32_top.vhd` line 1196: :code:`mtime_lo` is reset by the raw
  :code:`rstn_i` rather than the synchronized :code:`rstn_sys` (design_015).
* **Open Logic** (10d65be), :code:`src/base/vhdl/olo_base_cc_status.vhd` line 83: :code:`RstOutI_Sync` is only assigned
  in the reset branch and never read (design_006).
* **PoC** (8c39b24), :code:`src/net/net_FrameChecksum.vhdl`: :code:`Out_Meta_Checksum` and :code:`Out_Meta_Length` are
  driven both by a process (lines 246 and 247) and by concurrent assignments (lines 368 and 369).
