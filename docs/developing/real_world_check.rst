.. _real_world_check:

Real World Check
----------------

The unit tests check each rule against small, hand-written files.
The real world check runs mhsg over complete open source projects to find problems those files miss:
constructs the parser does not support, crashes, and fixes that interact badly with each other.

The projects are listed in :code:`scripts/real_world_projects.yaml`.
Each project is pinned to a commit, so the results only change when mhsg changes.

Running the check
=================

.. code-block:: bash

   $ python scripts/real_world_check.py

The projects are cloned into :code:`.real_world_cache` the first time the check runs.
Later runs reuse the clones.

Each VHDL file is copied to a temporary directory, checked, fixed, and then fixed a second time.
The result for a file is one of:

+-----------------+-----------------------------------------------------------+
| Status          | Meaning                                                   |
+=================+===========================================================+
| OK              | Every step succeeded and the second fix changed nothing.  |
+-----------------+-----------------------------------------------------------+
| CRASH           | The check raised an exception.                            |
+-----------------+-----------------------------------------------------------+
| PARSE_ERROR     | The file could not be parsed.                             |
+-----------------+-----------------------------------------------------------+
| FIX_CRASH       | A fix raised an exception.                                |
+-----------------+-----------------------------------------------------------+
| FIX_BROKE_PARSE | The fixed file could not be parsed.                       |
+-----------------+-----------------------------------------------------------+
| NOT_IDEMPOTENT  | The second fix changed the file again.                    |
+-----------------+-----------------------------------------------------------+
| TIMEOUT         | A step took longer than the time limit.                   |
+-----------------+-----------------------------------------------------------+

The check exits with status 1 when a file has a status other than OK that is not listed as a known issue.
For each new failure it prints the error message, or the difference between the two fixes.

Options
=======

:code:`--project NAME`
   Only check this project. The option can be repeated.

:code:`--jobs N`, :code:`-j N`
   Number of files checked in parallel. The default is the number of CPUs.

:code:`--timeout SECONDS`
   Time allowed for each mhsg run. The default is 600 seconds.

:code:`--json FILE`
   Write every result, including the details of each failure, to a JSON file.

:code:`--verbose`, :code:`-v`
   Also list the files that pass.

:code:`--cache DIRECTORY`
   Where the projects are cloned.

Known issues
============

A failure that is tracked by an issue is listed under :code:`known_issues` for its project:

.. code-block:: yaml

   known_issues:
     # #71: empty signature in alias declarations
     AssertApiPkg.vhd: PARSE_ERROR

The file does not fail the run while it keeps that status.
When the issue is fixed, the check reports the file as a known issue that no longer occurs, and the entry should be removed.

Files that are not complete VHDL on their own, such as templates, are listed under :code:`exclude` and are not checked:

.. code-block:: yaml

   exclude:
     - scripts/ada/strings_maps_constants.head.vhdl

A project too large to check whole lists the directories that are checked under :code:`include`, as OpenTitan does:

.. code-block:: yaml

   include:
     - hw/ip/uart/rtl
     - hw/ip/prim/rtl

When to run it
==============

A full run takes a few hours (a single fix of a large package can take several minutes), so it is not part of the unit tests.
Use :code:`--project` to check one project.
Run it before a release, and after changes to the parser or to rules with fixes that move tokens between lines.

Design analysis check
=====================

:code:`scripts/real_world_design_check.py` runs design analysis, see :doc:`../design_analysis`, on configurations of
the synthesizable projects: three configurations of neorv32 and 56 entities of Open Logic, each with realistic generics.
It needs GHDL, Yosys and the GHDL plugin for Yosys.

.. code-block:: bash

   $ python scripts/real_world_design_check.py
   $ python scripts/real_world_design_check.py --design neorv32_top

The designs are listed in :code:`scripts/real_world_designs.yaml`, each with the findings that were reviewed and
are expected, and a comment that explains each one:

.. code-block:: yaml

   known:
   # Real: RstOutI_Sync is assigned in the reset branch only and never read
   - src/base/vhdl/olo_base_cc_status.vhd(83)design_006 -- Register rstouti_sync in olo_base_cc_status is never used

The check exits with status 1 when a design has a finding that is not known, or when design analysis does not run.
Known findings that are no longer found are reported, so the list can be updated.
Run it when a change touches the design rules or the netlist analysis.
