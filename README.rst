Multiple HDL Style Guide (MHSG)
===============================

**Style checks, lint and design analysis for VHDL, Verilog and SystemVerilog.**

.. image:: https://img.shields.io/github/tag/xTheBearx/vhdl-style-guide.svg?style=flat-square
   :target: https://github.com/xTheBearx/vhdl-style-guide
   :alt: Github Release

MHSG checks and fixes the coding style of hardware description files, lints them against coding standards such as
DO-254 and STARC, and analyzes whole designs with GHDL and Yosys for latches, loops, clock and reset domain crossings,
and logic that can never be reached.

Table of Contents
-----------------

*   `Credits`_
*   `Features`_
*   `Installation`_
*   `Usage`_
*   `Configuration`_
*   `Integration`_
*   `Known Limitations`_
*   `Documentation`_
*   `Contributing`_

Credits
-------

MHSG is a fork of `VHDL Style Guide (VSG) <https://github.com/jeremiah-c-leary/vhdl-style-guide>`_, created by
**Jeremiah C. Leary**. It started from VSG 3.35.0 and has been maintained as a separate project since 2026.

Everything MHSG does for VHDL style rests on VSG's work: its VHDL parser, its rules and how they are configured, its
fixing in phases, its output formats and its documentation. Thanks to Jeremiah C. Leary and to everyone who has
contributed to VSG over the years. If you only need style checks for VHDL, VSG remains the original and is actively
developed.

MHSG is distributed under the same GNU General Public License v3 as VSG; see ``LICENSE``. The Python package and the
command are named ``mhsg`` instead of ``vsg``; the ``-- vsg_off``, ``-- vsg_on`` and ``-- vsg_disable_next_line``
code tags of existing files are still recognized, alongside the ``mhsg_`` ones.

Features
--------

**Style checks for VHDL.** More than 1,100 rules for whitespace, blank lines, indentation, alignment, case, naming,
structure and line length, from VSG and new ones, such as the blank lines of generic and port maps, the order of
generics, commented-out code, a second line length limit and descriptive rule aliases. Violations are reported, and
most are fixed with ``--fix``.

**Style checks for Verilog and SystemVerilog.** More than 200 rules, read with `pyslang
<https://github.com/MikePopoloski/pyslang>`_: indentation, whitespace, blank lines, alignment, the structure of always
blocks, case statements, begin and end, generate blocks and labels, naming, literals, declarations and comments. Code
in inactive ``ifdef`` branches and macro bodies is checked too. Files ending in ``.sv``, ``.svh``, ``.v`` and ``.vh``
are SystemVerilog; VHDL and SystemVerilog files can be checked in one run.

**Lint mode.** ``--lint`` and ``--lint_only`` report design problems that a single file shows, such as latches,
incomplete sensitivity lists, unreachable case choices and states never entered. Findings are labelled with the
checks of a rule set and have the severities Error, Warning and Note:

=============== ==========================================================================================
Rule set        Covers
=============== ==========================================================================================
``do254``       The DO-254 Users Group coding standards (DO254-UG-001), the default
``do254_plus``  ``do254`` and further good practice for state machines, numeric types and synthesis
``starc``       The STARC RTL Design Style Guide: 273 of its 613 items have rules, the rest are listed for review
``cdc``         Clock and reset domain crossing checks, CDC-001 to CDC-011
=============== ==========================================================================================

SystemVerilog files are linted with slang semantics, and optionally with Verilator, all the files of a run compiled
together. A rule set can also be a YAML file of your own.

**Design analysis.** ``--design`` elaborates the whole design with GHDL and Yosys and reports what no single file
shows, at the lines of the source files, with 48 design rules:

* latches, combinational loops, multiple drivers, constant and unused registers, logic depth and tri-state buses;
* clock domain crossings: unsynchronized signals, logic before synchronizers, buses without a safe scheme,
  reconvergence of separately synchronized signals, generated and gated clocks, and a full crossing report;
* resets: asynchronous release, internally generated resets and reset domain crossings, with isolation signals
  declared and checked;
* black boxes, declared by role or archetype, with libraries for AMD Xilinx, Microchip, Altera and Lattice primitives;
* design for test, with the test mode and scan shift inputs held;
* with SymbiYosys, branches that can never be taken from reset, states of state machines never entered, and state
  machines that can never return to their reset state.

VHDL, Verilog, SystemVerilog and mixed designs are read; SystemVerilog designs need the yosys-slang plugin.

**Waivers and reports.** Any finding can be waived with a justification, and waivers are listed in the reports.
Reports record the versions of the tools and the configuration used. ``--qualify`` runs the qualification suite of a
rule set and writes a tool qualification report, expected against actual, for certification.

Installation
------------

MHSG needs Python 3.12 or later. Once it is released on PyPI, it can be installed with **uv** or **pip**:

.. code-block:: bash

    uv tool install mhsg
    pip install mhsg

Until then, install the latest development version from GitHub:

.. code-block:: bash

    uv tool install git+https://github.com/xTheBearx/vhdl-style-guide
    pip install git+https://github.com/xTheBearx/vhdl-style-guide

Style checks and lint mode need nothing else. Design analysis needs further tools on the path:

================================== ========================================================================
Tool                               Needed for
================================== ========================================================================
GHDL, Yosys and the GHDL plugin    ``--design``, for example the Ubuntu packages ``ghdl yosys yosys-plugin-ghdl``
yosys-slang plugin                 Design analysis of SystemVerilog designs
SymbiYosys                         The formal rules design_025, design_047 and design_048
Verilator                          Optional SystemVerilog lint, sv_lint_011
================================== ========================================================================

The `OSS CAD Suite <https://github.com/YosysHQ/oss-cad-suite-build>`_ has all of them.

Usage
-----

Check files, and fix what can be fixed:

.. code-block:: bash

    mhsg -f src/*.vhd rtl/*.sv
    mhsg -f src/*.vhd rtl/*.sv --fix

Lint, with the default DO-254 rule set or another one:

.. code-block:: bash

    mhsg -f src/fifo.vhd --lint_only
    mhsg -f rtl/*.sv --lint_only --rule_set starc

The report shows each finding with the check of the rule set, the rule and the solution:

.. code-block:: text

    Total Rules Checked: 178
    Total Violations:    16
      Error   :     0
      Warning :     3
      Note    :    13
    -----------------------------+------------+------------+--------------------------------------
      Rule                       |  severity  |  line(s)   | Solution
    -----------------------------+------------+------------+--------------------------------------
      DO254-DR10 (lint_041)      | Warning    |          1 | Start the file with a header comment
      DO254-DR6 (port_004)       | Note       |          6 | Use 8 spaces for indent

Analyze a whole design, described in the ``design`` section of a configuration file, and write the clock domain
crossing report:

.. code-block:: bash

    mhsg --design -c design.yaml
    mhsg --design -c design.yaml --cdc_report cdc.txt

Run the qualification suite of a rule set:

.. code-block:: bash

    mhsg --qualify do254 --qualify_report qualification.txt

Other options give the output format (``-of mhsg|syntastic|summary``), JUnit, JSON and GitLab code quality reports
(``-j``, ``-js``, ``--quality_report``), the configuration of a rule (``-rc``), predefined styles (``--style``) and
parallel jobs (``-p``). ``mhsg --help`` lists them all.

.. image:: https://github.com/xTheBearx/vhdl-style-guide/blob/master/docs/img/fixing_single_file.gif

Configuration
-------------

Rules are configured in JSON or YAML files given with ``-c``; later files take precedence. A configuration can
disable rules, change their options and severity, list the files to check, waive findings and describe the design:

.. code-block:: yaml

    rule:
      global:
        indent_size: 4
      length_001:
        length: 120
    design:
      top: fifo_top
      libraries:
        - name: work
          files: [src/fifo_pkg.vhd, src/*.vhd]
      generics:
        DEPTH: 16
      cdc:
        clocks:
          sys_clk: u_pll.clk_out1

The default indent is 4 spaces and the default line length 80. Local rules written in Python can be added with
``-lr``, using the existing rules as templates.

Integration
-----------

MHSG runs in continuous integration with its JUnit and JSON outputs, and in editors through the syntastic output
format. Here is an example of a ``.pre-commit-config.yaml`` file; the hook checks VHDL files, and ``files`` adds
Verilog and SystemVerilog ones:

.. code-block:: yaml

  repos:
    - repo: https://github.com/xTheBearx/vhdl-style-guide
      rev: <release tag>
      hooks:
        - id: mhsg
          files: \.(vhd|vhdl|sv|svh|v|vh)$

Known Limitations
-----------------

* The VHDL parser does not process embedded PSL or VHDL-2019.
* Design analysis checks what GHDL and Yosys synthesize: logic synthesis removes, such as delay chains, is checked in
  lint mode instead.
* The formal rules can leave branches and states undecided within their time limits, such as states reached only
  after a long counter.
* Vendor libraries for black boxes were written from the vendors' guides; their port names have not been checked
  against a vendor installation.

The backlog of known gaps is in ``docs/developing/backlog.rst``, and the bugs found in the tools MHSG uses are in
``docs/developing/dependency_issues.rst``.

Documentation
-------------

The documentation is in the ``docs`` directory: every rule, the configuration, lint mode, design analysis, black
boxes, the rule sets and their coverage, and the qualification suites. Build it with:

.. code-block:: bash

    uv run --group docs sphinx-build docs build/docs/html

The `VSG documentation <http://vhdl-style-guide.readthedocs.io/en/latest/index.html>`_ also applies to the VHDL style
rules, with ``vsg`` read as ``mhsg``.

Contributing
------------

Contributions of any size are welcome: bug reports, feature requests, improvements and pull requests. Please open an
issue or pull request at https://github.com/xTheBearx/vhdl-style-guide; see ``docs/contributing.rst`` for details.
AI-assisted contributions are welcome when they are disclosed, understood by the submitter and backed by tests; see
the AI-Assisted Contributions section there.

The project is managed with `uv <https://docs.astral.sh/uv/>`_. Install the locked development dependencies, then run
the tests, the style checks and the build:

.. code-block:: bash

    git clone https://github.com/xTheBearx/vhdl-style-guide.git
    cd vhdl-style-guide
    uv sync
    uv run pytest
    uv run pre-commit run --all-files
    uv build
