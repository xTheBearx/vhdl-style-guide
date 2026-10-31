.. include:: includes.rst

Range Constraint Rules
----------------------

range_constraint_100
####################

|phase_2| |error| |whitespace|

Alias: :code:`range_constraint_space_before_range_keyword`

This rule checks for a single space before the **range** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

  subtype my_range is natural     range 0 to 7;

**Fix**

.. code-block:: vhdl

  subtype my_range is natural range 0 to 7;

range_constraint_101
####################

|phase_2| |error| |whitespace|

Alias: :code:`range_constraint_space_after_range_keyword`

This rule checks for a single space after the **range** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

  subtype my_range is natural range     0 to 7;

**Fix**

.. code-block:: vhdl

  subtype my_range is natural range 0 to 7;

range_constraint_500
####################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`range_constraint_range_keyword_case`

This rule checks the **range** keyword in range constraints has the proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   subtype t_range is natural RANGE 1 to 0;

**Fix**

.. code-block:: vhdl

   subtype t_range is natural range 1 to 0;
