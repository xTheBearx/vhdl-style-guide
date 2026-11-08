.. _gpu_simulation:

GPU Simulation Plan
===================

A plan, not yet started (2026-11-07): compiling a design for simulation on a CUDA GPU.

MHSG compiles a design for simulation on a CUDA GPU by building on an open-source GPU simulator, GEM or its fork
Jacquard, rather than writing one: MHSG already elaborates VHDL, Verilog, SystemVerilog and mixed designs with GHDL and
Yosys, and adds the synthesis to the simulator's gate library, the checks that a design can run there, the stimulus
and the comparison with a CPU simulator.

Goal and scope
--------------

:code:`mhsg --simulate` compiles the design of the :code:`design` section into a form a CUDA GPU runs, runs a test on
it, and checks the outputs. The GPU engines simulate the synthesized design cycle by cycle, as a two-valued gate
netlist: a register-transfer model of the hardware, not the event-driven semantics of a VHDL or Verilog simulator.

A GPU is faster in two cases, and slower outside them:

* **A large design**: GEM reports 5 to 40 times the speed of the leading CPU simulators, and up to 64 times in its
  paper, on designs of hundreds of thousands of gates and more. A small entity runs faster on GHDL or Verilator, as
  starting the GPU and mapping the design cost more than the run.
* **Many tests of one design at once**: RTLflow runs each stimulus in its own GPU thread, and reports 40 times an
  80-thread CPU with 65,536 stimuli on NVDLA. Random tests with many seeds, and regressions, gain the most.

Out of scope: timing simulation, the testbench language features that are not hardware (files, waits, assertions with
messages), and replacing the CPU simulators, which stay the reference for every GPU result.

Engines
-------

Jacquard is the first choice: it runs GEM's model on CUDA and also on a CPU backend, which lets the tests run in CI
without a GPU, and it reacts to the design's outputs through cosimulation. GEM stays the reference it is checked
against; RTLflow is the option for many stimuli of one design.

+------------------------+---------------------------+-----------------------------+-------------------------------+--------------------+------------+
| Engine                 | How it simulates          | Input                       | Stimulus                      | GPUs               | License    |
+========================+===========================+=============================+===============================+====================+============+
| `Jacquard`_            | GEM's virtual Boolean     | Behavioral Verilog or       | VCD replay; cosimulation with | CUDA, HIP (AMD),   | Apache-2.0 |
|                        | processor, extended       | SystemVerilog through       | SPI, UART, JTAG, Wishbone and | Metal, CPU         |            |
|                        |                           | embedded Yosys with         | APB models on the GPU         |                    |            |
|                        |                           | read_slang, or an aigpdk    |                               |                    |            |
|                        |                           | gate netlist                |                               |                    |            |
+------------------------+---------------------------+-----------------------------+-------------------------------+--------------------+------------+
| `GEM`_ (NVIDIA         | Gate netlist in           | aigpdk gate netlist from    | VCD replay only               | CUDA               | Apache-2.0 |
| Research, DAC 2025)    | and-inverter cells mapped | Yosys or Design Compiler    |                               |                    |            |
|                        | to a virtual manycore     |                             |                               |                    |            |
|                        | Boolean processor         |                             |                               |                    |            |
+------------------------+---------------------------+-----------------------------+-------------------------------+--------------------+------------+
| `RTLflow`_ (ICPP 2022) | Verilator's C++ model     | Verilog read by Verilator   | Batches of stimuli, thousands | CUDA, sm_80 by     | MIT        |
|                        | transpiled to CUDA        |                             | at once                       | default            |            |
|                        | kernels, one thread per   |                             |                               |                    |            |
|                        | stimulus                  |                             |                               |                    |            |
+------------------------+---------------------------+-----------------------------+-------------------------------+--------------------+------------+
| GHDL, Verilator (CPU)  | Event-driven (GHDL) or    | VHDL, Verilog,              | Full testbenches              | None               | GPL-2.0,   |
|                        | cycle-based (Verilator)   | SystemVerilog               |                               |                    | LGPL-3.0   |
+------------------------+---------------------------+-----------------------------+-------------------------------+--------------------+------------+

None reads VHDL: MHSG converts VHDL with GHDL, as design analysis already does, and hands the engines Verilog or a
gate netlist.

The flow
--------

The first two steps are what design analysis does today; the rest is new, and the synthesis and mapping are cached, as
they take longer than a CPU simulator's compile but are paid once per design.

#. **Read the design** of the :code:`design` section: VHDL through GHDL, Verilog and SystemVerilog through read_slang,
   mixed designs, generics, black box declarations.
#. **Check it can run on the GPU**, with the design rules and new ones: no latches, synchronous logic, clock gates to
   replace, models for black boxes, see the next section. A design that cannot run gets findings at its lines, not a
   failed run.
#. **Map the memories** with Yosys :code:`memory_libmap` to the RAM cells of the aigpdk library, and report each memory
   that falls back to registers, which is slow.
#. **Synthesize to the aigpdk cells** with Yosys (:code:`synth -flatten`, :code:`dfflibmap`, :code:`abc`), and keep the
   gate netlist.
#. **Check the gate netlist** against the RTL: an equivalence check with Yosys and SymbiYosys, or a short run of both
   on a CPU simulator.
#. **Map to the engine**: the GPU partitioning of Jacquard or GEM, cached under the design's hash.
#. **Prepare the stimulus**: a VCD of the inputs recorded from a CPU run of the testbench, stimulus generators
   synthesized into the design, or Jacquard's peripheral models.
#. **Run on the GPU**, as many instances as the stimuli allow.
#. **Compare** the outputs with a CPU reference, cycle by cycle at the ports, and report the first difference with its
   time and signal, plus the run time on both.

What the engines cannot run
---------------------------

The engines run synthesizable, synchronous hardware; most of what they cannot run, MHSG can already find, so it is
reported before a run rather than discovered in one.

+---------------------------+--------------------------------+--------------------------------------------------------+
| Not supported             | Example                        | What MHSG does                                         |
+===========================+================================+========================================================+
| VHDL testbenches, and     | :code:`wait for`, file reads,  | Runs the testbench once on GHDL or Verilator and       |
| testbench code in general | :code:`report`,                | records the DUT's inputs as a VCD to replay; or uses   |
|                           | :code:`$display`               | synthesizable stimulus generators; or Jacquard's       |
|                           |                                | cosimulation for interfaces it models                  |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Latches                   | A case statement without a     | Reported by design_002, as today; a GPU run is refused |
|                           | default                        | until it is fixed or waived                            |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Asynchronous logic,       | A ring oscillator, an          | Combinational loops by design_003; asynchronous resets |
| combinational loops       | asynchronous reset released at | turned into synchronous ones for simulation, and said  |
|                           | any time                       | so in the report                                       |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Clock gates in the RTL    | :code:`gclk <= clk and en`     | Found by design_012, and replaced with the CKLNQD cell |
|                           |                                | of the aigpdk library                                  |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Black boxes               | Vendor primitives, IP cores    | Need a synthesizable model; the black box declarations |
|                           |                                | name the ports, and a missing model stops the run with |
|                           |                                | the list of boxes                                      |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Four-valued logic         | X and Z, uninitialized         | Two values only (Jacquard adds X propagation): initial |
|                           | registers                      | values come from resets or are set to 0, and the       |
|                           |                                | report says which registers had none                   |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Delays and timing         | :code:`after 2 ns`             | Ignored, as synthesis does; Jacquard's SDF timing is   |
|                           |                                | out of scope                                           |
+---------------------------+--------------------------------+--------------------------------------------------------+
| Asynchronous memory reads | A register file read without a | Mapped to registers and multiplexers, which is slow    |
|                           | clock                          | for large memories; reported with its size             |
+---------------------------+--------------------------------+--------------------------------------------------------+

Delivery plan
-------------

Steps 1 to 3 need no GPU and run in CI on Jacquard's CPU backend; step 4 onwards needs a machine with an NVIDIA GPU.
Each step merges only when its tests pass.

#. **Prototype outside MHSG.** Take three designs by hand through the flow: a small FSM of the tests, Open Logic's
   olo_base_fifo_async, and neorv32. Exit: each runs on Jacquard's CPU backend and on a GPU with its outputs equal to
   GHDL's, and a short report gives the time of each step and where the flow broke.
#. **Gate netlist from the design section.** :code:`mhsg --sim_netlist FILE` writes the aigpdk netlist: memory mapping,
   synthesis, and the readiness checks of the previous section as findings. Exit: the netlists of the test designs and
   of the real-world designs that synthesize are equivalent to their RTL.
#. **Stimulus by recording.** Run the testbench on GHDL (or Verilator for Verilog), record the DUT's ports as a VCD, and
   replay it. Exit: replaying on the CPU backend gives the outputs GHDL gave, for the test designs.
#. **mhsg --simulate on the GPU.** Runs the engine found on the path or set under :code:`tools`, caches the mapping,
   compares the outputs with the recording, and reports the first difference and the run times. Exit: the three
   designs of step 1 pass on a GPU, and neorv32 runs a program faster than on GHDL.
#. **Many stimuli.** Synthesizable stimulus generators with a seed per instance, thousands of instances in one run, and
   a summary of the instances that failed. Exit: a random test of the FIFO with 10,000 seeds finishes faster on the GPU
   than the same seeds on the CPU, one after another.
#. **Interactive tests.** Jacquard's cosimulation for interfaces it models, and a batch interface for testbenches that
   answer the design every few cycles. Exit: neorv32 boots from a modelled SPI flash and prints over a modelled UART.
#. **CI and benchmarks.** A self-hosted GPU runner for the GPU tests, and a benchmark of the real-world designs on GPU
   and CPU with their times. Exit: the benchmark runs on every release.

Decide after step 1 whether to go on: if the prototype is not faster on the designs that matter to you, steps 2 and 3
still give a gate netlist and recorded stimulus, which are useful on their own, and the rest waits.

Risks and open questions
------------------------

* **No GPU in the development sessions or in GitHub's hosted CI.** The cloud sessions have no NVIDIA device, so the GPU
  steps can only be run on your machine or on a GPU runner you provide; Jacquard's CPU backend keeps the rest testable.
  Open question: which GPU, and can it host a self-hosted runner?
* **Speed on your designs is unknown.** The published speed-ups are for large designs and many stimuli; a VHDL design
  of a few thousand gates, run once, will likely be slower on the GPU. Step 1 measures this before anything is built
  into MHSG.
* **Testbenches are the hard part.** Recording and replaying only works for testbenches that do not react to the
  design. Reactive VHDL testbenches, such as those of OSVVM and UVVM, need cosimulation or rewriting the stimulus as
  synthesizable generators. Open question: which testbenches do you want to run?
* **Semantics differ from VHDL simulation.** Two-valued logic, no delays and synchronous resets mean a GPU run can pass
  where GHDL shows an X or a race; every result is checked against a CPU run until the flow has a record.
* **Synthesis quality sets the speed.** GEM recommends a commercial synthesis tool; Yosys works, but its netlists may
  run slower.
* **Young dependencies.** GEM was published in 2025 and Jacquard is newer; both may change. MHSG calls them as external
  programs, as it does GHDL and Yosys, and pins the versions it is tested with.
* **Scope.** A simulator flow is a new direction for a style and lint tool; it could live in a separate package that
  shares the design section, to keep MHSG's dependencies unchanged for those who do not need it.

Sources
-------

* `GEM`_ and its `usage guide <https://github.com/NVlabs/GEM/blob/HEAD/usage.md>`_: flow, aigpdk library, limitations
* `GEM: GPU-Accelerated Emulator-Inspired RTL Simulation
  <https://research.nvidia.com/publication/2025-06_gem-gpu-accelerated-emulator-inspired-rtl-simulation>`_, DAC 2025
* `Jacquard`_ and its `accepted RTL surface <https://gpu-eda.github.io/Jacquard/accepted-rtl.html>`_
* `RTLflow`_ and `From RTL to CUDA: A GPU Acceleration Flow for RTL Simulation with Batch Stimulus
  <https://research.nvidia.com/publication/2022-08_rtl-cuda-gpu-acceleration-flow-rtl-simulation-batch-stimulus>`_,
  ICPP 2022
* `FOSSi Foundation on GEM's release <https://fossi-foundation.org/blog/2025-07-15-ecl87>`_

.. _Jacquard: https://github.com/gpu-eda/Jacquard
.. _GEM: https://github.com/NVlabs/GEM
.. _RTLflow: https://github.com/dian-lun-lin/RTLflow
