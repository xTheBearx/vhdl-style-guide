.. _qualification:

Tool Qualification
==================

A tool whose output is not checked by hand, such as a lint tool that replaces part of a code review, needs evidence
that it finds what it should, for the qualification DO-254 and DO-330 ask for. :code:`--qualify` runs the
qualification suite of a built in rule set: examples of code for each rule of the set, with the findings recorded
for them, and reports, case by case, the expected findings against the actual ones.

.. code-block:: bash

   $ mhsg --qualify do254 --qualify_report qualification.json
   Qualification of rule set DO-254 version 1

   PASS     lint_009 (DO254-SS4) on examples/lint/rule_009_test_input.vhd
   ...
   PASS     design_001 (DO254-CP1, DO254-CP7, DO254-CP13) on clean design
   ...

   Summary: 315 passed, 0 failed, 0 not run

   Run
     Tools: mhsg 3.36.0, Python 3.12.3, pyslang 12.1.0, Verilator 5.020 2024-01-01 rev (Debian 5.020-1), GHDL 4.1.0 (Ubuntu 4.1.0+dfsg-0ubuntu2.1) [Dunoon edition], Yosys 0.33 (git sha1 2584903a060)
     Command line: --qualify do254 --qualify_report qualification.json

Each case runs one example on its own, as MHSG checks a file in lint mode with the rule set, with every phase, and
compares the findings of one rule with those recorded: the line and the message of each. An example on which a rule
reports nothing, such as a fixed version, checks that the rule does not report correct code. The rules of design
analysis run on example designs, and need GHDL and Yosys, and the rules that report Verilator's warnings need
Verilator; without them their cases are not run, and the report says so. The exit status is 1 if a case fails.

:code:`--qualify_report` also writes the report to a file: JSON for a file ending in .json, otherwise text. The report
records the rule set and the suite with their versions and SHA-256 digests, the cases with their checks, the rules
of the set that have no example, and the record of the run, see :ref:`the record of the run <run_record>`.

The suite
---------

The suites are in :code:`mhsg/qualification`: one manifest for each rule set, named after it, and the examples.
:code:`scripts/make_qualification_suite.py` makes them from the test inputs of MHSG: the inputs of each rule's tests and
their fixed versions, the SystemVerilog test inputs on which a rule reports something, examples written for rules that
have no test input, in :code:`scripts/qualification_examples`, and the test designs for the rules of design analysis.
It records what each rule finds in each example as the expected result.

The expected results are the reviewed behaviour of MHSG: when a rule changes, make the suite again and review the
differences of the manifests before committing them. A difference that is not intended is a defect.
