Usage
=====

MHSG is a both a command line tool and a python package.
The command line tool can be invoked with:

.. code-block:: text

   $ mhsg
   usage: Multiple HDL Style Guide (MHSG) [-h] [-f FILENAME [FILENAME ...]]
                                 [--index_files INDEX_FILES [INDEX_FILES ...]]
                                 [-lr LOCAL_RULES [LOCAL_RULES ...]]
                                 [-c CONFIGURATION [CONFIGURATION ...]] [--fix]
                                 [-fp FIX_PHASE] [-j JUNIT] [-js JSON]
                                 [-of {mhsg,syntastic,summary}] [-b]
                                 [-oc OUTPUT_CONFIGURATION]
                                 [-rc RULE_CONFIGURATION]
                                 [--output_options OUTPUT_OPTIONS]
                                 [--style {indent_only,jcl}] [-v] [-ap]
                                 [--fix_only FIX_ONLY] [--stdin] [--stdout]
                                 [--quality_report QUALITY_REPORT] [-p JOBS]
                                 [--debug]
                                 [FILENAME ...]

   Analyzes VHDL files for style guide violations. Reference documentation is
   located at: http://vhdl-style-guide.readthedocs.io/en/latest/index.html

   positional arguments:
     FILENAME              File to analyze

   options:
     -h, --help            show this help message and exit
     -f FILENAME [FILENAME ...], --filename FILENAME [FILENAME ...]
                           File to analyze
     --index_files INDEX_FILES [INDEX_FILES ...]
                           Files which are only read to find declarations and
                           instantiations, for example for port_028, and are not
                           analyzed
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
     -b, --backup          Creates a copy of input file for comparison with fixed
                           version.
     -oc OUTPUT_CONFIGURATION, --output_configuration OUTPUT_CONFIGURATION
                           Write configuration to file name.
     -rc RULE_CONFIGURATION, --rule_configuration RULE_CONFIGURATION
                           Display configuration of a rule
     --output_options OUTPUT_OPTIONS
                           Write a description of every option, with its type,
                           allowed values and default, to file name (JSON), for
                           building an options dialog.
     --style {indent_only,jcl}
                           Use predefined style: indent_only (Only applies
                           indent rules), jcl (Coding style preferred by
                           Jeremiah Leary)
     -v, --version         Displays version information
     -ap, --all_phases     Do not stop when a violation is detected.
     --fix_only FIX_ONLY   Restrict fixing via JSON file.
     --stdin               Read VHDL input from stdin, disables all other file
                           selections, disables multiprocessing
     --stdout              With --fix, write the fixed code to stdout instead of
                           the file and the report to stderr. Requires a single
                           input.
     --quality_report QUALITY_REPORT
                           Create code quality report for GitLab
     -p JOBS, --jobs JOBS  number of parallel jobs to use, default is the number
                           of cpu cores
     --debug               Displays verbose debug information

**Command Line Options**

+-------------------------------+-------------------------------------------------+
| Option                        |  Description                                    |
+-------------------------------+-------------------------------------------------+
| -f FILENAME                   | The VHDL file to be analyzed or fixed.          |
|                               | Multiple files can be passed through this       |
|                               | option.                                         |
|                               | The path to each file can also be specified.    |
|                               | File globbing is also supported.                |
+-------------------------------+-------------------------------------------------+
| --stdin                       | Reads VHDL file input from standard in put      |
|                               | instead of reading from a file or files. Can be |
|                               | useful for using with other tools such as       |
|                               | editors that can interact through stdin/stdout  |
|                               | for diagnostics                                 |
+-------------------------------+-------------------------------------------------+
| --stdout                      | Used with --fix. Writes the fixed code to       |
|                               | standard out instead of back to the file, and   |
|                               | the report to standard error. The exit status   |
|                               | is 0 unless the code could not be processed.    |
|                               | Allows MHSG to be used as an editor formatter.  |
+-------------------------------+-------------------------------------------------+
| --local_rules LOCAL_RULES     | Directories of additional rules not in the base |
|                               | set.                                            |
+-------------------------------+-------------------------------------------------+
| --configuration CONFIGURATION | JSON or YAML file(s) which alters the behavior  |
|                               | of MHSG.  Configuration can also include a list |
|                               | files to analyze.  Any combination of JSON and  |
|                               | YAML files can be passed.  Each will be         |
|                               | processed in order from left to right.          |
+-------------------------------+-------------------------------------------------+
| --fix                         | Update issues found.                            |
|                               | Replaces current file with updated one.         |
+-------------------------------+-------------------------------------------------+
| --fix_phase                   | Applies for all phases up to and including      |
|                               | this phase.  Analysis will then be performed    |
|                               | on all phases.                                  |
+-------------------------------+-------------------------------------------------+
| --junit                       | Filename of JUnit XML file to generate.         |
|                               | The path to the file can also be specified, but |
|                               | the destination directory must exist.           |
+-------------------------------+-------------------------------------------------+
| --json                        | Filename of JSON file to generate.              |
|                               | The path to the file can also be specified, but |
|                               | the destination directory must exist.           |
+-------------------------------+-------------------------------------------------+
| --output_format               | Configures the sdout output format.             |
|                               |   mhsg -- standard MHSG output                  |
|                               |   syntastic -- format compatible with the       |
|                               |   syntastic VIM module                          |
|                               |   summary -- Minimal output useful when running |
|                               |   on multiple files                             |
+-------------------------------+-------------------------------------------------+
| --backup                      | Creates a copy of the input file before         |
|                               | applying any fixes.  This can be used to        |
|                               | compare the fixed file against the original.    |
|                               | NOTE:  This is only valid when using --fix.     |
+-------------------------------+-------------------------------------------------+
| --output_configuration        | Writes a JSON configuration file of the current |
|                               | run.  It includes a file_list, local_rules (if  |
|                               | used), and how every rule was configured.       |
|                               | This configuration can be fed back into MHSG.   |
|                               | The path to the file can also be specified, but |
|                               | the destination directory must exist.           |
+-------------------------------+-------------------------------------------------+
| --rule_configuration          | Displays the configuration of a rule.           |
+-------------------------------+-------------------------------------------------+
| --output_options              | Writes a JSON description of every option, with |
|                               | its type, allowed values, default and help      |
|                               | text, for programs that build an options        |
|                               | dialog. See :ref:`options-description`.         |
+-------------------------------+-------------------------------------------------+
| --style                       | Use a built in coding style.                    |
+-------------------------------+-------------------------------------------------+
| --version                     | Displays the version of MHSG.                   |
+-------------------------------+-------------------------------------------------+
| --all_phases                  | Executes all phases without stopping if a       |
|                               | violation is found.                             |
|                               | NOTE: This is not valid with the --fix option.  |
+-------------------------------+-------------------------------------------------+
| --fix_only                    | Restrict which rules are fixed based on JSON    |
|                               | file.                                           |
+-------------------------------+-------------------------------------------------+
| --quality_report              | Write a quality report which can be used by     |
|                               | GitLab                                          |
+-------------------------------+-------------------------------------------------+
| --jobs                        | Restrict the number of cores used to run.  The  |
|                               | default is the number of cores available.       |
+-------------------------------+-------------------------------------------------+
| --debug                       | Print verbose debug information to assist with  |
|                               | debugging errors with MHSG.                     |
+-------------------------------+-------------------------------------------------+


Here is an example output running against a test file:

.. code-block:: text

   $ mhsg -f example/architecture-empty.vhd
   ================================================================================
   File:  example/architecture-empty.vhd
   ================================================================================
   Phase 1 of 7... Reporting
   Total Rules Checked: 83
   Total Violations:     3
     Error   :     3
     Warning :     0
   ----------------------------+------------+------------+--------------------------------------
     Rule                      |  severity  |  line(s)   | Solution
   ----------------------------+------------+------------+--------------------------------------
     port_021                  | Error      |         45 | Move the ( to the same line as the "port" keyword.
     instantiation_034         | Error      |        169 | Change to component instantiation
     generic_map_003           | Error      |        170 | Move the ( to the same line as the "generic map" keyword.
   ----------------------------+------------+--------------------------------------
   NOTE: Refer to online documentation at https://vhdl-style-guide.readthedocs.io/en/latest/index.html for more information.

MHSG will report the rule which is violated and the line number or group of lines where the violation occurred.
It also gives a suggestion on how to fix the violation.
The rules MHSG uses are grouped together into :doc:`phases`.
These phases follow the order in which the user would take to address the violations.
Each rule is detailed in the :doc:`rules` section.
The violation and the appropriate fix for each rule is shown.

The violations can be fixed manually, or use the **--fix** option to have MHSG update the file.

.. code-block:: text

   $ mhsg -f example/architecture-empty.vhd
   ================================================================================
   File:  example/architecture-empty.vhd
   ================================================================================
   Phase 7 of 7... Reporting
   Total Rules Checked: 378
   Total Violations:    0

If rule violations can not be fixed, they will be reported after fixing everything that can be mixed:

.. code-block:: text

   $ mhsg -f example/architecture-empty.vhd
   ================================================================================
   File:  example/architecture-empty.vhd
   ================================================================================
   Phase 1 of 7... Reporting
   Total Rules Checked: 83
   Total Violations:     1
     Error   :     1
     Warning :     0
   ----------------------------+------------+------------+--------------------------------------
     Rule                      |  severity  |  line(s)   | Solution
   ----------------------------+------------+------------+--------------------------------------
     instantiation_034         | Error      |        169 | Change to component instantiation
   ----------------------------+------------+--------------------------------------
   NOTE: Refer to online documentation at https://vhdl-style-guide.readthedocs.io/en/latest/index.html for more information.

Use Cases
#########

The following examples show how to perform certain tasks with MHSG.

Checking a single file
----------------------

.. code-block:: text

   $ mhsg -f fifo.vhd

Checking a single file over standard input
------------------------------------------

.. code-block:: text

   $ mhsg --stdin

Formatting code from standard input to standard output
------------------------------------------------------

This is how an editor can use MHSG as a formatter.

.. code-block:: text

   $ mhsg --stdin --fix --stdout < fifo.vhd > fifo.formatted.vhd

Checking multiple files using globbing
--------------------------------------

.. code-block:: text

   $ mhsg -f *.vhd

Checking multiple files in different directories
------------------------------------------------

.. code-block:: text

   $ mhsg -f fifos/src/*.vhd cpu_core/src/*.vhd usb_hub/src/*.vhd

Checking all files in a project
-------------------------------

.. code-block:: text

   $ find . -name "*.vhd" -exec mhsg -f {} \;

Integration with CI server
--------------------------

.. code-block:: text

   $ mhsg -f fifos/src/*.vhd --junit fifos/src/fifos_junit.xml

Fixing a single file
--------------------

.. code-block:: text

   $ mhsg -f fifo.vhd --fix

Fixing multiple files using globbing
------------------------------------

.. code-block:: text

   $ mhsg -f *.vhd --fix

Fixing all files in a project
-----------------------------

.. code-block:: text

   $ find . -name "*.vhd" -exec mhsg -f {} --fix \;

Error Codes
###########

One of the following error codes will be returned after running MHSG:

+------------+-------------------------------------------------+
| Error Code |  Description                                    |
+------------+-------------------------------------------------+
|     0      |  MHSG ran without encountering any errors and no|
|            |  rule violations were detected.                 |
+------------+-------------------------------------------------+
|     1      |  MHSG ran and detected a rule violation.        |
+------------+-------------------------------------------------+
|     2      |  An attempt was made to configure a rule which  |
|            |  was deprecated.                                |
+------------+-------------------------------------------------+
