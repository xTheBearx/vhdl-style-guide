.. include:: includes.rst

Type Mark Rules
---------------

type_mark_500
#############

|phase_6| |error| |case| |case_name|

Alias: :code:`type_mark_case`

This rule checks that the type marks without declarations in the current file have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

  signal my_sig : MY_TYPE_MARK;

**Fix**

.. code-block:: vhdl

  signal my_sig : my_type_mark;

type_mark_501
#############

|phase_6| |disabled| |error| |case| |case_name|

Alias: :code:`type_mark_conversion_case`

This rule checks the type mark in a type conversion has proper case.

A name followed by parentheses is a type conversion if it names a standard or IEEE type, such as **std_logic_vector** or **unsigned**,
or a type or subtype declared in one of the files checked in the same run.
Other names followed by parentheses are function calls or indexes and are not checked.
Type conversions to types declared in the same file are checked by :ref:`type_014` instead, which keeps them consistent with the declaration.

.. NOTE:: This rule is disabled by default.
   Configure it with the same case as :ref:`type_mark_500` to treat type conversions like other type marks.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   data <= STD_LOGIC_VECTOR(count);

**Fix**

.. code-block:: vhdl

   data <= std_logic_vector(count);
