.. include:: includes.rst

Interface Incomplete Type Declaration Rules
-------------------------------------------

interface_incomplete_type_declaration_500
#########################################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`interface_incomplete_type_declaration_type_keyword_case`

This rule checks the **type** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   generic (
     TYPE generic_data_type

**Fix**

.. code-block:: vhdl

   generic (
     type generic_data_type

interface_incomplete_type_declaration_501
#########################################

|phase_6| |error| |case| |case_name|

Alias: :code:`interface_incomplete_type_declaration_type_name_case`

This rule checks the type name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   generic (
     type GENERIC_DATA_TYPE

**Fix**

.. code-block:: vhdl

   generic (
     type generic_data_type

interface_incomplete_type_declaration_600
#########################################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`interface_incomplete_type_declaration_prefix`

This rule checks for valid prefixes of type names.

.. NOTE::  The default prefix is *gt_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic (
     type generic_data_type

**Fix**

.. code-block:: vhdl

   generic (
     type gt_generic_data_type

interface_incomplete_type_declaration_601
#########################################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`interface_incomplete_type_declaration_suffix`

This rule checks for valid suffixes of type names.

.. NOTE::  The default prefix is *_gt*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic (
     type generic_data_type

**Fix**

.. code-block:: vhdl

   generic (
     type generic_data_type_gt
