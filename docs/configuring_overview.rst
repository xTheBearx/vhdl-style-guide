Overview
========

MHSG can use a configuration file to alter its behavior and/or include a list of files to analyze.
This is accomplished by passing JSON and/or YAML file(s) through the **--configuration** command line argument.
This is the basic form of a configuration file in JSON:

.. code-block:: text

   {
     "file_list": [
       "fifo.vhd",
       {
         "source/spi.vhd": {
           "rule": {
             "ruleId_ruleNumber": "blah"
           }
         }
       },
       "$PATH_TO_FILE/spi_master.vhd",
       "$OTHER_PATH/src/*.vhd"
     ],
     "file_rules": [
       {
         "source/i2c.vhd": {
           "rule": {
             "ruleId_ruleNumber": "blah"
           }
         }
       }
     ],
     "local_rules":"$DIRECTORY_PATH",
     "rule": {
       "global": {
         "attributeName":"AttributeValue"
       },
       "group": {
         "group_name": {
           "attributeName":"AttributeValue"
         }
       }
       "ruleId_ruleNumber": {
         "attributeName":"AttributeValue"
       }
     }
   }

This is the basic form of a configuration file in YAML:

.. code-block:: yaml

   file_list:
     - fifo.vhd
     - source/spi.vhd:
         rule:
           ruleId_ruleNumber:
             attributeName: AttributeValue
     - $PATH_TO_FILE/spi_master.vhd
     - $OTHER_PATH/src/*.vhd
   file_rules:
     - source/i2c.vhd:
         rule:
           ruleId_ruleNumber:
             attributeName: AttributeValue
   local_rules: $DIRECTORY_PATH
   rule:
     global:
       attributeName: AttributeValue
     group:
       group_name:
         attributeName : AttributeValue
     ruleId_ruleNumber:
       attributeName: AttributeValue


It is not required to have **file_list**, **local_rules**, and **rule** defined in the configuration file.
Any combination can be defined, and the order does not matter.

.. NOTE:: All examples of configurations in this documentation use JSON.  However, YAML can be used instead.

file_list
---------

The file_list is a list of files that will be analyzed.
Environment variables will expanded.
File globbing is also supported.
The Environment variables will be expanded before globbing occurs.
This option can be useful when running MHSG over multiple files.

The file name will be converted to POSIX style using '/' as a separator for all platforms.

Rule configurations can be specified for each file by following the format of the **rule** configuration.

.. NOTE:: Defining rule configurations under the file_list will be deprecated at some point.
          Use the file_rules option instead.

file_rules
----------

The file_rules option allows for configuration of individual rules per file.
It uses the same format as file_list, but it does not add files to the list of files to analyze.
A file listed under this option has the configuration applied only when it is analyzed, for example because it was given with **-f**.

Environment variables are expanded and globbing is supported, so a pattern can apply a configuration to a group of files.
For example, this configuration allows upper case entity names in every file in a **test_hdl** directory:

.. code-block:: yaml

   file_rules:
     - '**/test_hdl/*.vhd':
         rule:
           entity_008:
             case: upper
           entity_012:
             case: upper

A file is matched however its path is written on the command line, for example **test_hdl/tb.vhd**, **./test_hdl/tb.vhd** or the absolute path.
If a file matches more than one entry, every matching configuration is applied in the order of the entries, so a later entry overrides an earlier one.
The configurations are applied after the **rule** section, so they override it for the files they match.

linesep
-------

The linesep is an optional settings for line separator.
Default is platform specific.
Logical values may be "\n" or "\r\n".

.. code-block:: yaml

   linesep: "\n"

local_rules
-----------

Local rules can be defined on the command line or in a configuration file.
If they are defined in both locations, the configuration will take precedence.

Either a single directory or a list of directories can be given:

.. code-block:: yaml

   local_rules:
     - $DIRECTORY_PATH_1
     - $DIRECTORY_PATH_2

The rules in every directory are loaded.
Rule identifiers must be unique across all of the directories.

rule
----

Any attribute of any rule can be configured.
Using **global** will set the attribute for every rule.
Using **group** will set attributes for groups of rules.
Each rule is addressable by using its unique **ruleId** and **ruleNumber** combination.  For example, whitespace_006 or port_010.
Each rule can also be addressed by its alias, see `Rule Aliases`_.

.. NOTE::
   If **global** and unique attributes are set at the same time, the unique attribute will take precedence.


Here are a list of attributes that can be altered for each rule:

+--------------+---------+--------------------------------------------------+
| Attribute    | Values  | Description                                      |
+==============+=========+==================================================+
| indent_size  | Integer | Sets the number of spaces for each indent level. |
+--------------+---------+--------------------------------------------------+
| phase        | Integer | Sets the phase the rule will run in.             |
+--------------+---------+--------------------------------------------------+
| disable      | Boolean | If set to True, the rule will not run.           |
+--------------+---------+--------------------------------------------------+
| fixable      | Boolean | If set to False, the violation will not be fixed |
+--------------+---------+--------------------------------------------------+

Rule Aliases
############

Every rule also has a descriptive alias, shown in the documentation of the rule and by the **-rc** option.
The alias can be used instead of the rule identifier wherever a rule is configured, including under **file_list** and **file_rules**.
These two configurations are equivalent:

.. code-block:: yaml

   rule:
     if_025:
       case: upper

.. code-block:: yaml

   rule:
     if_keyword_case:
       case: upper

Violations are still reported with the rule identifier.
Configuring the same rule with both its identifier and its alias in one configuration file is an error.

.. _reporting-single-rule-configuration:

Reporting Single Rule Configuration
-----------------------------------

The configuration for a single rule can be reported using the **-rc** option:

.. code-block:: text

   $ mhsg -rc entity_001
   {
     "rule": {
       "entity_001": {
         "alias": "entity_keyword_indent",
         "indent_size": 2,
         "phase": 4,
         "disable": false,
         "fixable": true
       }
     }
   }

MHSG will print the configuration for the rule given in a JSON format.
This configuration can be altered and added to a configuration file.
The rule can also be given by its alias, for example :code:`mhsg -rc entity_keyword_indent`.

Reporting Configuration for All Rules
-------------------------------------

Every rule configuration can be report and saved to a file using the **-oc** option:

.. code-block:: text

   $ mhsg -oc configuration.json

The output file will be in JSON format and can be modified and passed back to MHSG using the *-c* option.

Rule Configuration Priorities
-----------------------------

There are three ways to configure a rule.
From least to highest priority are:

* **[rule][global]**
* **[rule][group]**
* **[rule][<identifier>]**
* **[file_list][<filename>][rule][<identifier>]**.

If the same rule is defined in all four locations as in the example below, then the final setting will be equal to the highest priority.

.. code-block:: text

   {
     "file_list": [
       {
         "entity.vhd": {
           "rule": {
             "length_001":{
               "disable": true
             }
           }
        }
      },
      "architecture.vhd",
      "package.vhd"
     ],
     "rule":{
       "global":{
         "disable": true
       },
       "group":{
         "length": {
           "disable": false
         }
       },
       "rule": {
         "length_001":{
           "disable": false
         }
       }
     }
   }


In this example configuration, all rules are disabled by the **global** configuration.
Then rule **length_001** is enabled for the files **architecture.vhd**, **package.vhd** and **entity.vhd** by the **rule** configuration.
Then rule **length_001** is disabled for the file **entity.vhd**.

Example:  Disabling a rule
--------------------------

Below is an example of a JSON file which disables the rule **entity_004**

.. code-block:: json

   {
       "rule":{
           "entity_004":{
               "disable":true
           }
       }
   }

Use the configuration with the **--configuration** command line argument:

.. code-block:: text

   $ mhsg -f RAM.vhd --configuration entity_004_disable.json

Example: Setting the indent increment size for a single rule
------------------------------------------------------------

The indent increment size is the number of spaces an indent level takes.
It can be configured on an per rule basis...

.. code-block:: json

   {
       "rule":{
           "entity_004":{
               "indent_size":4
           }
       }
   }

Example: Setting the indent increment size for all rules
--------------------------------------------------------

Configure the indent size for all rules by setting the **global** attribute.

.. code-block:: json

   {
       "rule":{
           "global":{
               "indent_size":4
           }
       }
   }

Example: Enabling only indent rules
-----------------------------------

Configure the indent size for all rules by setting the **global** attribute.

.. code-block:: json

   {
       "rule": {
           "global": {
               "indent_size": 4
           },
           "group": {
               "indent": {
                   "disable": false
               }
           }
       }
   }
