.. _lint:

Lint Mode
=========

Besides style, MHSG can check VHDL for design problems such as latches, multiple drivers or incomplete case statements.
These lint checks only report; they never change the code.

The checks are grouped in rule sets, which map the checks of a coding standard to the MHSG rules that implement them.
The built in rule set, **do254**, implements the coding standards of the DO-254 Users Group position paper
*Best Practice VHDL Coding Standards for DO-254 Programs* (DO254-UG-001 Rev 1a).

Running lint mode
-----------------

.. code-block:: text

   $ mhsg -f fifo.vhd --lint
   $ mhsg -f fifo.vhd --lint_only
   $ mhsg -f fifo.vhd --lint_only --rule_set my_standard.yaml

+--------------+------------------------------------------------------------------------------------------+
| Option       | Effect                                                                                   |
+==============+==========================================================================================+
| --lint       | Runs the lint checks of the rule set in addition to the style rules.                     |
+--------------+------------------------------------------------------------------------------------------+
| --lint_only  | Runs only the rules of the rule set: its lint checks and the style rules it reuses.      |
+--------------+------------------------------------------------------------------------------------------+
| --rule_set   | The rule set: a built in name (default **do254**), the path of a YAML file, or **none**  |
|              | for every lint rule with its own severity and no labels.                                 |
+--------------+------------------------------------------------------------------------------------------+

The same can be set in a configuration file:

.. code-block:: yaml

   lint_only: true
   rule_set: do254

Lint rules run before the style phases and do not stop a run, so they report the same problems whatever the formatting.
A rule set can also reuse style rules, for example the indent rules for consistent indentation.
Those rules are reported with the severity of their check.

Fixing in lint mode
-------------------

Lint rules never change the code. With **--fix**, the style rules are fixed first and the lint checks then run on the fixed file,
so their line numbers refer to the fixed file.

The severity from a rule set only changes how a rule is reported and whether it fails the run.
Whether **--fix** fixes a rule still follows the rule's own severity, its default or the one in your configuration:

+----------------------+------------------------------------------------------------+------------------------------+
| Command              | Fixed                                                      | Lint checks                  |
+======================+============================================================+==============================+
| --fix                | The style rules, as without lint mode                      | Not run                      |
+----------------------+------------------------------------------------------------+------------------------------+
| --lint --fix         | The style rules, as without lint mode                      | Reported on the fixed file   |
+----------------------+------------------------------------------------------------+------------------------------+
| --lint_only --fix    | Only the style rules of the rule set, such as indentation  | Reported on the fixed file   |
|                      | and tabs for **do254**                                     |                              |
+----------------------+------------------------------------------------------------+------------------------------+

A rule set can also change which rules run: **do254** disables the rules that remove labels, since DR1 asks for labels.
Setting the severity of a rule in a configuration file replaces the severity from the rule set.

Output
------

Each violation is labelled with the check of the rule set, followed by the MHSG rule:

.. code-block:: text

   WARNING: fifo.vhd(14)DO254-SS4 (lint_009) -- Signal out1 is not assigned on every path of the combinational process, which infers a latch

The JSON output lists the checks of each violation under **checks**.

In lint mode there is a third severity, **Note**, which the DO-254 coding standards use for checks that only need to be examined.
A Note is reported like a warning and does not fail a run.

Lint checks can be disabled for a line or a region with code tags, like any other rule, see :doc:`code_tags`.
When a violation is accepted, the code tag is a good place to give the justification:

.. code-block:: vhdl

   -- mhsg_disable_next_line lint_012 synchronizer flip-flops have no reset by design
   sync_r <= async_in;

What the lint checks see
------------------------

The lint checks analyze one file at a time.
They know the declarations in the file, and the ports of entities and components in the other files of the run and the index files (see **index_file_list**).
They do not resolve types or evaluate generics, so they err on the side of not reporting:

* names declared outside the file, other than ports, are treated as unknown;
* statements in different if or case generate statements are not compared, since elaboration decides which exist;
* an if statement whose condition reads only constants and generics is treated as decided at elaboration.

Checks that need the whole elaborated design, such as clock domain crossings, are planned for a design analysis mode.

Rule set files
--------------

A rule set is a YAML file:

.. code-block:: yaml

   name: My standard
   prefix: MY
   version: "1"
   checks:
     LATCH:
       title: No latches
       severity: Error
       rules: [lint_009]
     TABS:
       title: No tabs
       severity: Warning
       rules: [whitespace_002]
     INDENT:
       title: Consistent indentation
       severity: Note
       groups: [indent]
     LABELS:
       title: Labelled concurrent statements
       rules: [concurrent_013]
       configuration:
         concurrent_005: {disable: true}

Each check has:

* **title** and **severity**, one of Error, Warning or Note, or a severity defined in the configuration;
* **rules** and **groups**: the rules that implement the check, by identifier and by rule group;
* **configuration**: options set on rules, for example to disable a rule that conflicts with the check;
* **enable**: false labels the rules without enabling them, for checks that need project settings first;
* **status**: for a check without rules, one of planned, design or manual.

A rule that implements checks of different severities gets the most severe one.

The DO-254 rule set
-------------------

This table is generated from :code:`mhsg/rule_sets/do254.yaml`.
DR13 lists the naming rules but does not enable them: configure the prefixes and suffixes of your project, then enable the naming rules.

.. include:: do254_coverage.rst
