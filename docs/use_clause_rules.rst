.. include:: includes.rst

Use Clause Rules
----------------

use_clause_001
##############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`use_clause_allowed_packages`

This rule checks for packages that have been restricted by the user.

|configuring_library_and_package_name_restriction_rules_link|

.. NOTE:: This rule is disabled by default.

.. NOTE:: This rule is configured to restrict the std_logic_arith package by default.

**Violation**

.. code-block:: vhdl

   use ieee.std_logic_arith.all;

use_clause_500
##############

|phase_6| |error| |case| |case_name|

Alias: :code:`use_clause_library_name_case`

This rule checks the library name called out in the selected name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   use IEEE.std_logic_1164.all;

   use my_LIB.all;

**Fix**

.. code-block:: vhdl

   use ieee.std_logic_1164.all;

   use my_lib.all;

use_clause_501
##############

|phase_6| |error| |case| |case_name|

Alias: :code:`use_clause_package_name_case`

This rule checks the package name called out in the selected name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   use ieee.STD_LOGIC_1164.all;

**Fix**

.. code-block:: vhdl

   use ieee.std_logic_1164.all;

use_clause_502
##############

|phase_6| |error| |case| |case_name|

Alias: :code:`use_clause_item_name_case`

This rule checks the item name called out in the selected name has proper case.

.. NOTE:: The item is usually declared in a package in another file, so this rule cannot know what kind of item it is or how it is spelled where it is declared.
   If items are imported whose declarations follow a different case, for example constants in upper case, either:

   * set :code:`case` to :code:`upper_or_lower` to accept items in all upper case or all lower case, or
   * list patterns matching those items in :code:`regex_exceptions`, for example :code:`'c_'` for constants named with a :code:`c_` prefix.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   use my_lib.Increment;

**Fix**

.. code-block:: vhdl

   use my_lib.increment;

use_clause_503
##############

|phase_6| |error| |case| |case_keyword|

Alias: :code:`use_clause_all_keyword_case`

This rule checks the **all** keyword called out in the selected name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   use ieee.std_logic_1164.ALL;

**Fix**

.. code-block:: vhdl

   use ieee.std_logic_1164.all;
