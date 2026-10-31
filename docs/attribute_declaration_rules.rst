.. include:: includes.rst

Attribute Declaration Rules
---------------------------

attribute_declaration_100
#########################

|phase_2| |error| |whitespace|

Alias: :code:`attribute_declaration_space_after_keyword_and_colon`

This rule checks for a single space after the following elements:  **attribute** keyword and colon.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   attribute   max_delay :   time;

**Fix**

.. code-block:: vhdl

   attribute max_delay : time;

attribute_declaration_101
#########################

|phase_2| |error| |whitespace|

Alias: :code:`attribute_declaration_space_before_colon`

This rule checks for at least a single space before the colon.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   attribute max_delay: time;

**Fix**

.. code-block:: vhdl

   attribute max_delay : time;

attribute_declaration_300
#########################

|phase_4| |error| |indent|

Alias: :code:`attribute_declaration_attribute_keyword_indent`

This rule checks the indent of the **attribute** keyword.

**Violation**

.. code-block:: vhdl

   signal sig1 : std_logic;
      attribute max_delay : time;

**Fix**

.. code-block:: vhdl

   signal sig1 : std_logic;
   attribute max_delay : time;

attribute_declaration_500
#########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`attribute_declaration_attribute_keyword_case`

This rule checks the **attribute** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   ATTRIBUTE max_delay : time;

**Fix**

.. code-block:: vhdl

   attribute max_delay : time;

attribute_declaration_501
#########################

|phase_6| |error| |case| |case_name|

Alias: :code:`attribute_declaration_identifier_case`

This rule checks the *identifier* has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   attribute MAX_DELAY : time;

**Fix**

.. code-block:: vhdl

   attribute max_delay : time;

attribute_declaration_502
#########################

|phase_6| |error| |case| |case_name|

Alias: :code:`attribute_declaration_type_mark_case`

This rule checks the *type_mark* has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   attribute max_delay : TIME;

**Fix**

.. code-block:: vhdl

   attribute max_delay : time;
