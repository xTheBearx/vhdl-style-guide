.. include:: includes.rst

Unspecified Type Indication Rules
---------------------------------

unspecified_type_indication_100
###############################

|phase_2| |error| |whitespace|

Alias: :code:`unspecified_type_indication_space_after_type_keyword`

This rule checks for a single space after the **type** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is access type    is private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;

unspecified_type_indication_101
###############################

|phase_2| |error| |whitespace|

Alias: :code:`unspecified_type_indication_space_after_is_keyword`

This rule checks for a single space after the **is** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is access type is    private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;

unspecified_type_indication_500
###############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`unspecified_type_indication_type_keyword_case`

This rule checks the **type** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is access TYPE is private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;

unspecified_type_indication_501
###############################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`unspecified_type_indication_is_keyword_case`

This rule checks the **is** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_data is access type IS private;

**Fix**

.. code-block:: vhdl

   type t_data is access type is private;
