Multiple HDL Style Guide (MHSG)
===============================

**Coding style enforcement for VHDL.**

.. image:: https://img.shields.io/github/tag/xTheBearx/vhdl-style-guide.svg?style=flat-square
   :target: https://github.com/xTheBearx/vhdl-style-guide
   :alt: Github Release

About this project
------------------

MHSG is a fork of `VHDL Style Guide (VSG) <https://github.com/jeremiah-c-leary/vhdl-style-guide>`_,
created by Jeremiah C. Leary, and has been maintained as a separate project since 2026.
It is distributed under the same GNU General Public License v3; see ``LICENSE``.

Compared with VSG, the Python package and command are named ``mhsg`` instead of ``vsg``.
The ``-- vsg_off``, ``-- vsg_on`` and ``-- vsg_disable_next_line`` code tags in existing source files are still recognized,
alongside the new ``mhsg_`` versions.

.. image:: https://github.com/xTheBearx/vhdl-style-guide/blob/master/docs/img/vim_macro.gif

Table of Contents
-----------------

*   `Overview`_
*   `Key Benefits`_
*   `Key Features`_
*   `Known Limitations`_
*   `Installation`_
*   `Usage`_
*   `Documentation`_
*   `Contributing`_

Overview
--------

MHSG was created after participating in a code review where a real issue in the code was masked by a coding style issue.
A finding was created for the style issue, while the real issue was missed.
When the code was re-reviewed, the real issue was discovered.

Depending on your process, style issues can take a lot of time to resolve.

#. Create finding/ticket/issue
#. Disposition finding/ticket/issue
#. Fix
#. Verify fix

Spending less time on style issues leaves more time to analyze the substance of the code.
This ultimately reduces the amount of time performing code reviews.
It also allows reviewers to focus on the substance of the code.
This will result in a higher quality code base.

Key Benefits
------------

* Define VHDL coding standards
* Makes coding standards visible to everyone
* Improve code reviews
* Quickly bring code up to current standards

MHSG allows the style of the code to be defined and enforced over part or the entire code base.
Configurations allow for multiple coding standards.

Key Features
------------

* Command line tool

  * integrate into continuous integration flow with JUnit output

* Reports and fixes issues found

  * whitespace

    * horizontal
    * vertical

  * upper and lower case
  * keyword alignments
  * etc...

* Fully configurable rules via JSON or YAML configuration file

  * Disable rules
  * Alter behavior of existing rules

* Localize rule sets

  * Create your own rules using python
  * Use existing rules as a template
  * Fully integrates into base rule set

* Built in styles

  * Use existing style or create your own

Known Limitations
-----------------

MHSG is a continual work in progress.
As such, this version has the following known limitations:

* Parser will not process embedded PSL
* Parser will not process VHDL 2019

Installation
------------

Once released on PyPI, MHSG can be installed with **uv** or **pip**.

.. code-block:: bash

    uv tool install mhsg
    pip install mhsg

Until then, install the latest development version directly from GitHub.

.. code-block:: bash

    uv tool install git+https://github.com/xTheBearx/vhdl-style-guide
    pip install git+https://github.com/xTheBearx/vhdl-style-guide

The latest development version can be cloned...

.. code-block:: bash

    git clone https://github.com/xTheBearx/vhdl-style-guide.git

The project is managed with `uv <https://docs.astral.sh/uv/>`_.
Install the locked development dependencies, then run the tests, the style checks and the build:

.. code-block:: bash

    uv sync
    uv run pytest
    uv run pre-commit run --all-files
    uv build

Design analysis (**--design**) also needs GHDL, Yosys and the GHDL plugin for Yosys, which are system packages,
for example ``ghdl yosys yosys-plugin-ghdl`` on Ubuntu.

Usage
-----

MHSG is a both a command line tool and a python package.
The command line tool can be invoked with:

.. code-block:: bash

   $ mhsg
   usage: Multiple HDL Style Guide (MHSG) [-h] [-f FILENAME [FILENAME ...]] [-lr LOCAL_RULES [LOCAL_RULES ...]] [-c CONFIGURATION [CONFIGURATION ...]] [--fix]
                                 [-fp FIX_PHASE] [-j JUNIT] [-js JSON] [-of {mhsg,syntastic,summary}] [-b] [-oc OUTPUT_CONFIGURATION]
                                 [-rc RULE_CONFIGURATION] [--style {indent_only,jcl}] [-v] [-ap] [--fix_only FIX_ONLY] [--stdin]
                                 [--quality_report QUALITY_REPORT] [-p JOBS] [--debug]
                                 [FILENAME ...]

   Analyzes VHDL files for style guide violations. Reference documentation is located at: http://vhdl-style-guide.readthedocs.io/en/latest/index.html

   positional arguments:
     FILENAME              File to analyze

   options:
     -h, --help            show this help message and exit
     -f FILENAME [FILENAME ...], --filename FILENAME [FILENAME ...]
                           File to analyze
     -lr LOCAL_RULES [LOCAL_RULES ...], --local_rules LOCAL_RULES [LOCAL_RULES ...]
                           Path(s) to local rule directories
     -c CONFIGURATION [CONFIGURATION ...], --configuration CONFIGURATION [CONFIGURATION ...]
                           JSON or YAML configuration file(s)
     --fix                 Fix issues found
     -fp FIX_PHASE, --fix_phase FIX_PHASE
                           Fix issues up to and including this phase
     -j JUNIT, --junit JUNIT
                           Extract Junit file
     -js JSON, --json JSON
                           Extract JSON file
     -of {mhsg,syntastic,summary}, --output_format {mhsg,syntastic,summary}
                           Sets the output format.
     -b, --backup          Creates a copy of input file for comparison with fixed version.
     -oc OUTPUT_CONFIGURATION, --output_configuration OUTPUT_CONFIGURATION
                           Write configuration to file name.
     -rc RULE_CONFIGURATION, --rule_configuration RULE_CONFIGURATION
                           Display configuration of a rule
     --style {indent_only,jcl}
                           Use predefined style
     -v, --version         Displays version information
     -ap, --all_phases     Do not stop when a violation is detected.
     --fix_only FIX_ONLY   Restrict fixing via JSON file.
     --stdin               Read VHDL input from stdin, disables all other file selections, disables multiprocessing
     --quality_report QUALITY_REPORT
                           Create code quality report for GitLab
     -p JOBS, --jobs JOBS  number of parallel jobs to use, default is the number of cpu cores
     --debug               Displays verbose debug information

Here is an example output running against a test file:

.. image:: https://github.com/xTheBearx/vhdl-style-guide/blob/master/docs/img/fixing_single_file.gif

pre-commit Integration
----------------------

Here is an example of ``.pre-commit-config.yaml`` file:

.. code-block:: yaml

  repos:
    - repo: https://github.com/xTheBearx/vhdl-style-guide
      rev: <release tag>
      hooks:
        - id: mhsg

Documentation
-------------

The documentation is in the ``docs`` directory of this repository.
The upstream VSG documentation hosted at `read-the-docs <http://vhdl-style-guide.readthedocs.io/en/latest/index.html>`_ also applies, with ``vsg`` replaced by ``mhsg``.

Contributing
------------

I welcome any contributions to this project.
No matter how small or large.

There are several ways to contribute:

* Bug reports
* Code base improvements
* Feature requests
* Pull requests

Please open an issue or pull request at https://github.com/xTheBearx/vhdl-style-guide.
See ``docs/contributing.rst`` for more details on contributing.
AI-assisted contributions are welcome when they are disclosed, understood by the submitter and backed by tests; see the AI-Assisted Contributions section there.
