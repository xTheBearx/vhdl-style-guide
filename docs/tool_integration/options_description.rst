.. _options-description:

Options Description
-------------------

Programs which configure MHSG, for example an editor plugin with an options dialog, can read a description of every option from a JSON file.
It lists every rule with its options, and for each option its type, allowed values, default value, a label and a help text.

The description of the built in rules is included in the repository as :code:`docs/mhsg_options.json`.
To include local rules, or for the version of MHSG that is installed, write it with the **--output_options** command line option:

.. code-block:: text

   $ mhsg --output_options mhsg_options.json
   $ mhsg --output_options mhsg_options.json -lr ~/local_rules

The options of the dialog are saved in an ordinary configuration file, see :doc:`../configuring_overview`.
Only the options that differ from their default need to be written.
To show the values of an existing configuration in the dialog, read them from the configuration file, or from the output of **--output_configuration**.

File format
###########

The file is a JSON object with these keys:

+--------------------+-----------------------------------------------------------------------------------------+
| Key                | Contents                                                                                |
+====================+=========================================================================================+
| format             | Always :code:`mhsg-options`.                                                            |
+--------------------+-----------------------------------------------------------------------------------------+
| format_version     | The version of this format, currently 1.                                                |
|                    | It is increased when a change could break a program which reads the file.               |
+--------------------+-----------------------------------------------------------------------------------------+
| mhsg_version       | The version of MHSG which wrote the file.                                               |
+--------------------+-----------------------------------------------------------------------------------------+
| documentation_url  | The location of the documentation pages named by :code:`documentation` and              |
|                    | :code:`option_documentation`.                                                           |
+--------------------+-----------------------------------------------------------------------------------------+
| settings           | The configuration keys which are not rule options, such as :code:`file_list`.           |
+--------------------+-----------------------------------------------------------------------------------------+
| rule_scopes        | Where rule options can be set: for one rule, for a rule group, or for every rule.       |
+--------------------+-----------------------------------------------------------------------------------------+
| rule_groups        | The rule groups, each with the identifiers of its rules.                                |
+--------------------+-----------------------------------------------------------------------------------------+
| definitions        | The definitions of the options, by identifier.                                          |
+--------------------+-----------------------------------------------------------------------------------------+
| rules              | The rules, sorted by identifier.                                                        |
+--------------------+-----------------------------------------------------------------------------------------+

Rules
#####

Each rule is an object with these keys:

* **id**: the rule identifier, such as :code:`port_028`.
* **alias**: the descriptive alias, which can be used instead of the identifier in a configuration.
* **category**: the part of the identifier before the number, such as :code:`port`. It can be used to arrange the rules in a tree.
* **groups**: the rule groups the rule belongs to.
* **summary**: the first paragraph of the rule documentation.
* **documentation**: the documentation page of the rule, relative to :code:`documentation_url`. It is null for local rules.
* **option_documentation**: the page that explains the options shared by rules of this kind, if there is one.
* **options**: the options of the rule.

Every rule has the options :code:`disable`, :code:`fixable`, :code:`severity`, :code:`phase`, :code:`indent_style`, :code:`indent_size` and :code:`user_error_message`.
Rules which are disabled by default have the default :code:`true` for :code:`disable`.

Each option is an object with these keys:

* **name**: the key of the option in a configuration file.
* **default**: the value the rule uses when the option is not configured.
* **definition**: the identifier of its entry in :code:`definitions`.

The value of an option is set in a configuration file under :code:`rule`, the rule identifier or alias, and the name of the option:

.. code-block:: yaml

   rule:
     port_028:
       disable: false
       order: [direction, name]

Definitions
###########

Options with the same meaning share a definition, so many rules refer to the same one, for example :code:`case` or :code:`number_of_spaces`.
A definition is an object with these keys:

* **type**: one of the types below.
* **label**: a short title for the option.
* **description**: a help text.
* **values**: the allowed values of an :code:`enum`.
* **item_type**: the type of the items of a :code:`list`, :code:`string` or :code:`list_of_strings`.
* **nullable**: true if the option can also be null, which means that it is not set.
* **minimum** and **maximum**: the range of an :code:`integer`, where there is one.
* **format**: :code:`regex` for strings which are regular expressions.

+-------------------+------------------------------------------------------------------------------------------+
| Type              | Value                                                                                    |
+===================+==========================================================================================+
| boolean           | :code:`true` or :code:`false`.                                                           |
+-------------------+------------------------------------------------------------------------------------------+
| integer           | A whole number.                                                                          |
+-------------------+------------------------------------------------------------------------------------------+
| string            | Any text.                                                                                |
+-------------------+------------------------------------------------------------------------------------------+
| enum              | One of the strings in :code:`values`.                                                    |
+-------------------+------------------------------------------------------------------------------------------+
| integer_or_string | A whole number, or a string with a comparison such as :code:`>=1`, :code:`<3` or         |
|                   | :code:`2+`. Used by :code:`number_of_spaces`.                                            |
+-------------------+------------------------------------------------------------------------------------------+
| list              | A list of items of :code:`item_type`.                                                    |
+-------------------+------------------------------------------------------------------------------------------+

Options of local rules which MHSG has no metadata for get a definition from their default value, with an empty description.

Settings
########

Each entry of :code:`settings` describes a configuration key which is not a rule option.
It has the keys of a definition, plus :code:`path`, the list of keys that lead to the setting in a configuration file, and :code:`default`.
Some settings have a type of their own:

* **file_rule_list**: a list of single key objects, which map a file name or pattern to a configuration with a :code:`rule` key. See :code:`file_rules` in :doc:`../configuring_overview`.
* **severity_map**: an object which maps the name of a custom severity to an object with a :code:`type` key, :code:`error` or :code:`warning`.
* **design_library_list**: a list of objects with a :code:`name` key and a :code:`files` list of files and glob patterns, or a :code:`files_from` file listing them, and optionally an :code:`exclude` list of patterns. See :doc:`../design_analysis`.
* **generic_map**: an object which maps generic names to values.
* **vendor_library_list**: a list of vendor names, maps with :code:`vendor` and optionally :code:`family` and :code:`path`, or maps with :code:`library` and :code:`files`. See :doc:`../design_analysis`.
* **black_box_map**: an object which maps black box types, or instance paths, to declarations. See :doc:`../design_analysis`.
* **cdc_constraints**: an object with the keys :code:`clocks`, :code:`clock_groups`, :code:`inputs` and :code:`waivers`. An input maps to its domain, or to a map of its :code:`domain` and :code:`bits` (:code:`bus` or :code:`independent`). See :doc:`../design_analysis`.
* **indent_table**: an object which maps a token group to token names, each with a :code:`token` and an :code:`after` value. The default is the complete built in table.
