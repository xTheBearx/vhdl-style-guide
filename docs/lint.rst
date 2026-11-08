.. _lint:

Lint Mode
=========

Besides style, MHSG can check VHDL, Verilog and SystemVerilog for design problems such as latches, multiple drivers or incomplete case statements.
These lint checks only report; they never change the code.
For SystemVerilog and Verilog files the lint rules are :code:`sv_lint_001` to :code:`sv_lint_010`,
:code:`sv_lint_017` and :code:`sv_lint_018`, which report what slang finds when it elaborates the file,
:code:`sv_lint_014` to :code:`sv_lint_016`, which check the files of a run against each other, and
:code:`sv_lint_011` to :code:`sv_lint_013`, which report Verilator's warnings when Verilator is installed, see
:doc:`systemverilog`. The **do254** rule set labels them with
its checks too.

Verilog files, :code:`.v` and :code:`.vh`, are read as Verilog-2005: a check whose rules all need SystemVerilog, such
as one asking for always_latch, does not apply to them, and the coverage tables below mark those rules
"(SystemVerilog only)", see :doc:`verilog_2005`.

The checks are grouped in rule sets, which map the checks of a coding standard to the MHSG rules that implement them.
There are four built in rule sets:

* **do254** implements the coding standards of the DO-254 Users Group position paper
  *Best Practice VHDL Coding Standards for DO-254 Programs* (DO254-UG-001 Rev 1a).
* **do254_plus** includes do254 and adds further good practice: the synthesizable subset, numeric types, clocks and
  state machines, traceability, and the `HDLbits VHDL coding guidelines <https://www.hdlbits.com/guides/>`_.
  Where those conflict with DO-254, DO-254 wins; for example every register needs a reset.
* **cdc** holds the clock domain crossing, clock and reset checks of design analysis, see :doc:`design_analysis`.
* **starc** follows the STARC *RTL Design Style Guide for Verilog HDL* for Verilog and SystemVerilog files, see
  `The STARC rule set`_.

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
|              | for every lint rule with its own severity and no labels. Giving a rule set turns on      |
|              | lint mode, as **--lint** does.                                                           |
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

.. _run_record:

**Record of the run.** So that a result can be reproduced and shown to an auditor, the reports record how they were
made: the versions of MHSG, Python and pyslang, and of GHDL and Yosys for design analysis; the command line; each
configuration file with its SHA-256 digest, and a digest of the configuration they make together; the lint mode; and
each rule set with its version and digest. The JSON output (:code:`--json`) has it under **run**:

.. code-block:: json

   {
     "files": [],
     "run": {
       "mhsg": "3.36.0",
       "python": "3.12.3",
       "pyslang": "12.1.0",
       "command_line": ["-f", "fifo.vhd", "-c", "mhsg.yaml", "--rule_set", "do254", "--json", "fifo.json"],
       "configuration_files": [{"file": "mhsg.yaml", "sha256": "e10324..."}],
       "configuration_sha256": "31b0f5...",
       "lint_mode": "lint",
       "rule_sets": [{"name": "DO-254", "version": "1", "sha256": "253f82..."}]
     }
   }

The JUnit report (:code:`--junit`) has the same in the properties of its test suite, such as
:code:`<property name="mhsg.version" value="3.36.0" />`. With :code:`--design`, :code:`--json` writes the findings of
design analysis, with the versions of GHDL and Yosys and whether Yosys has the yosys-slang plugin, and the clock domain
crossing report ends with the record too, see :doc:`design_analysis`. The text output on the terminal, which is read
rather than kept, and the code quality report, whose format has no place for it, do not have the record.

In lint mode there is a third severity, **Note**, which the DO-254 coding standards use for checks that only need to be examined.
A Note is reported like a warning and does not fail a run.

Lint checks can be disabled for a line or a region with code tags, like any other rule, see :doc:`code_tags`.
When a violation is accepted, the code tag is a good place to give the justification; a waiver, below, also lists it in the reports:

.. code-block:: vhdl

   -- mhsg_disable_next_line lint_012 synchronizer flip-flops have no reset by design
   sync_r <= async_in;

.. _waivers:

Waivers
-------

A code tag leaves no record of what it disabled. A waiver accepts a finding with a justification and keeps it in the
reports, for a review or an audit. Waivers are listed in the **waivers** section of a configuration:

.. code-block:: yaml

   waivers:
     - rule: lint_012
       file: rtl/sync/*.vhd
       message: "*sync_r*"
       justification: The synchronizer flip-flops have no reset by design
       reviewer: A. Reviewer
     - rule: sv_lint_unused
       file: rtl/core/alu.sv
       line: [112, 140]
       justification: Spare signals kept for the next revision

* **rule** is a rule identifier, an alias, or a pattern such as ``sv_lint_*``. Required.
* **justification** says why the finding is accepted. Required: a waiver without one stops the run.
* **file** narrows the waiver to files: a pattern without a directory, such as ``*_sync.vhd``, matches the file name;
  one with a directory matches the path, relative to where MHSG runs.
* **line** narrows it to a line or a list of lines, and **message** to findings whose message matches a pattern.
* **reviewer** names who accepted it.

A waived finding does not fail the run and is not reported as a violation. It is listed with its waiver, its
justification and its reviewer: in the text output under **Waived**, in the JSON output (:code:`--json`) under
**waived** for each file, in the JUnit report (:code:`--junit`) in the system-out of the file's test case, and in the
code quality report (:code:`--quality_report`) with the severity info:

.. code-block:: text

   Waived:              1
     lint_012 line 42: Register sync_r has no reset
       waiver 1, reviewed by A. Reviewer: The synchronizer flip-flops have no reset by design

A waiver whose rule ran on a file it names, but which matched no finding there, is reported on standard error, as it
may be out of date:

.. code-block:: text

   WARNING: waiver 2 (rule sv_lint_005, file rtl/core/alu.sv) matched no finding; it may be out of date

Waivers apply to every rule, lint and style alike, and to the findings of design analysis. They do not stop
:code:`--fix` from changing the code a fixable rule reports; a code tag does. The crossings of clock domain analysis
have their own waivers, in the cdc section of the design, see :doc:`design_analysis`.

What the lint checks see
------------------------

The lint checks analyze one file at a time.
They know the declarations in the file, and the ports of entities and components in the other files of the run and the index files (see **index_file_list**).
They do not resolve types or evaluate generics, so they err on the side of not reporting:

* names declared outside the file, other than ports, are treated as unknown;
* statements in different if or case generate statements are not compared, since elaboration decides which exist;
* an if statement whose condition reads only constants and generics is treated as decided at elaboration.

Checks that need the whole elaborated design run in design analysis, see :doc:`design_analysis`.

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

A rule set can include others with **extends**, by built in name or by a path relative to its file.
The checks of an included set keep their own labels, and options set by the including set win:

.. code-block:: yaml

   name: My standard
   prefix: MY
   extends: do254
   checks:
     ...

A rule that implements checks of different severities gets the most severe one.

The DO-254 rule set
-------------------

This table is generated from :code:`mhsg/rule_sets/do254.yaml`. The rules named sv\_ implement the checks for
SystemVerilog and Verilog files, see :doc:`systemverilog`; under do254, sv_statement_008 nests at most 4 deep and
sv_comment_007 asks for 20 percent of comments, the limits of lint_030 and lint_042. sv_case_013 and lint_037, and lint_017 and
lint_027, find the state machines whose enumerated type the file declares or, in lint mode, another file of the run,
such as a package.
DR13 lists the naming rules but does not enable them: configure the prefixes and suffixes of your project, then enable the naming rules.
Some checks have options a project usually sets: the fields of the file header (lint_041, **required_fields**), the
share of comments (lint_042, **minimum_percent**), the nesting limit (lint_030, **nesting_limit**), the direction of
vector ranges (lint_031, **direction**) and the parts of names ignored when a signal is compared with its port
(lint_040, **strip_prefixes** and **strip_suffixes**).

.. include:: do254_coverage.rst

The DO-254 plus rule set
------------------------

This table is generated from :code:`mhsg/rule_sets/do254_plus.yaml`. It lists the checks the set adds; it also runs every check of **do254**.
Two checks need settings for your project: REQ needs the pattern of your requirement tags (the :code:`pattern` option of lint_018),
and FSMSAFE checks synthesis attributes only when its :code:`attributes` option lists them.

.. include:: do254_plus_coverage.rst

The STARC rule set
------------------

This table is generated from :code:`mhsg/rule_sets/starc.yaml`. Each numbered item of the STARC
*RTL Design Style Guide for Verilog HDL* (Second Version, 2006) is a check labelled with its number, such as
STARC-2.1.5.1, with a short paraphrase of the item as its title; the guide has the full text and the reasons.
Choose it for Verilog and SystemVerilog files:

.. code-block:: text

   $ mhsg -f rtl/*.v rtl/*.sv --rule_set starc

The severity follows the level of the item in the guide: a Rule is an error, Recommendation 1 a warning,
Recommendation 2 and 3 and Suggestions notes. The set uses the guide's own limits where a rule implements them:
lines of up to 110 characters and indentation of 2 spaces. A configuration file can change them, as for any rule.

Most items are not implemented yet: the per-file checks are planned with the SystemVerilog rules, the clock and reset
checks with design analysis of Verilog designs, and the items about synthesis and timing scripts, design management
or judgement are left to review. Items the rules of VHDL design analysis already check, such as clock domain
crossings and gated clocks, are labelled in design analysis of VHDL designs too.

.. include:: starc_coverage.rst
