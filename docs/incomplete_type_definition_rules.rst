.. include:: includes.rst

Incomplete Type Definition Rules
--------------------------------

incomplete_type_definition_100
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_before_of_keyword`

This rule checks for a single space before the **of** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is array (type is range <>)    of type is private;

**Fix**

.. code-block:: vhdl

   type t_data is array (type is range <>) of type is private;

incomplete_type_definition_101
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_of_keyword`

This rule checks for a single space after the **of** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is file of    type is private;

**Fix**

.. code-block:: vhdl

   type t_data is file of type is private;

incomplete_type_definition_102
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_access_keyword`

This rule checks for a single space after the **access** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is access    type is private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;

incomplete_type_definition_103
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_file_keyword`

This rule checks for a single space after the **file** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is file    of type is private;

**Fix**

.. code-block:: vhdl

   type t_data is file of type is private;

incomplete_type_definition_104
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_range_keyword`

This rule checks for a single space after the **range** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is range    <>;

**Fix**

.. code-block:: vhdl

   type t_data is range <>;

incomplete_type_definition_105
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_units_keyword`

This rule checks for a single space after the **units** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is units    <>;

**Fix**

.. code-block:: vhdl

   type t_data is units <>;

incomplete_type_definition_106
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_array_keyword`

This rule checks for whitespace after the **array** keyword.
The default of no whitespace matches unbounded_array_definition_100.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is array (type is range <>) of type is private;
   type t_data is array     (type is range <>) of type is private;

**Fix**

.. code-block:: vhdl

   type t_data is array(type is range <>) of type is private;
   type t_data is array(type is range <>) of type is private;

incomplete_type_definition_107
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_before_dot`

This rule checks for whitespace before the **.** of a floating incomplete type definition.
The default of a single space matches the form :code:`range <> . <>` used in the LRM.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is range <>. <>;
   type t_data is range <>    . <>;

**Fix**

.. code-block:: vhdl

   type t_data is range <> . <>;
   type t_data is range <> . <>;

incomplete_type_definition_108
##############################

|phase_2| |error| |whitespace|

Alias: :code:`incomplete_type_definition_space_after_dot`

This rule checks for whitespace after the **.** of a floating incomplete type definition.
The default of a single space matches the form :code:`range <> . <>` used in the LRM.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is range <> .<>;
   type t_data is range <> .    <>;

**Fix**

.. code-block:: vhdl

   type t_data is range <> . <>;
   type t_data is range <> . <>;

incomplete_type_definition_500
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_private_keyword_case`

This rule checks the **private** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is PRIVATE;

**Fix**

.. code-block:: vhdl

   type t_data is private;

incomplete_type_definition_501
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_range_keyword_case`

This rule checks the **range** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is RANGE <>;

**Fix**

.. code-block:: vhdl

   type t_data is range <>;

incomplete_type_definition_502
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_units_keyword_case`

This rule checks the **units** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is UNITS <>;

**Fix**

.. code-block:: vhdl

   type t_data is units <>;

incomplete_type_definition_503
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_array_keyword_case`

This rule checks the **array** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is ARRAY (type is range <>) of type is private;

**Fix**

.. code-block:: vhdl

   type t_data is array (type is range <>) of type is private;

incomplete_type_definition_504
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_of_keyword_case`

This rule checks the **of** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is array (type is range <>) OF type is private;

**Fix**

.. code-block:: vhdl

   type t_data is array (type is range <>) of type is private;

incomplete_type_definition_505
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_access_keyword_case`

This rule checks the **access** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is ACCESS type is private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;

incomplete_type_definition_506
##############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`incomplete_type_definition_file_keyword_case`

This rule checks the **file** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is FILE of type is private;

**Fix**

.. code-block:: vhdl

   type t_data is file of type is private;
