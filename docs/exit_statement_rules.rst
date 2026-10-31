.. include:: includes.rst

Exit Rules
----------

exit_statement_300
##################

|phase_4| |error| |indent|

Alias: :code:`exit_statement_exit_keyword_indent`

This rule checks the indent of the **exit** keyword.

**Violation**

.. code-block:: vhdl

   end if;

     exit;

**Fix**

.. code-block:: vhdl

   end if;

   exit;

exit_statement_301
##################

|phase_4| |error| |indent|

Alias: :code:`exit_statement_label_indent`

This rule checks the indent of the label.

**Violation**

.. code-block:: vhdl

   end if;

     exit_label : exit;

**Fix**

.. code-block:: vhdl

   end if;

   exit_label : exit;

exit_statement_500
##################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`exit_statement_exit_keyword_case`

This rule checks the **exit** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   EXIT when condition;

**Fix**

.. code-block:: vhdl

   exit when condition;

exit_statement_501
##################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`exit_statement_when_keyword_case`

This rule checks the **when** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   exit WHEN condition;

**Fix**

.. code-block:: vhdl

   exit when condition;
