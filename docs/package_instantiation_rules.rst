.. include:: includes.rst

Package Instantiation Rules
---------------------------

package_instantiation_001
#########################

|phase_1| |error| |structure|

Alias: :code:`package_instantiation_identifier_on_same_line_as_package_keyword`

This rule checks the new package identifier is on the same line as the **package** keyword.

**Violation**

.. code-block:: vhdl

   package
   my_pkg is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_002
#########################

|phase_1| |error| |structure|

Alias: :code:`package_instantiation_is_keyword_on_same_line_as_identifier`

This rule checks the **is** keyword is on the same line as the new package identifier.

**Violation**

.. code-block:: vhdl

   package my_pkg
   is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_003
#########################

|phase_1| |error| |structure|

Alias: :code:`package_instantiation_new_keyword_on_same_line_as_is_keyword`

This rule checks the **new** keyword is on the same line as the **is** keyword.

**Violation**

.. code-block:: vhdl

   package my_pkg is
   new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_004
#########################

|phase_1| |error| |structure|

Alias: :code:`package_instantiation_uninstantiated_name_on_same_line_as_new`

This rule checks the uninstantiated package name is on the same line as the **new** keyword.

**Violation**

.. code-block:: vhdl

   package my_pkg is new
   my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_100
#########################

|phase_2| |error| |whitespace|

Alias: :code:`package_instantiation_space_after_package_keyword`

This rule checks for a single space between the **package** keyword and the new package identifier.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   package    my_pkg is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_101
#########################

|phase_2| |error| |whitespace|

Alias: :code:`package_instantiation_space_before_is_keyword`

This rule checks for a single space between the new package identifier and the **is** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg    is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_102
#########################

|phase_2| |error| |whitespace|

Alias: :code:`package_instantiation_space_between_is_and_new`

This rule checks for a single space between the **is** keyword and the **new** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is    new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_103
#########################

|phase_2| |error| |whitespace|

Alias: :code:`package_instantiation_space_after_new_keyword`

This rule checks for a single space between **new** keyword and the uninstantiated package name.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is new    my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_200
#########################

|phase_3| |error| |blank_line|

Alias: :code:`package_instantiation_lines_above_package_keyword`

This rule checks for blank lines or comments above the **package** keyword.

|configuring_previous_line_rules_link|

The default style is :code:`no_code`.

**Violation**

.. code-block:: vhdl

   library ieee;
   package my_pkg is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   library ieee;

   package my_pkg is new my_generic_pkg

package_instantiation_201
#########################

|phase_3| |error| |blank_line|

Alias: :code:`package_instantiation_blank_line_below_first_line`

This rule checks for blank lines below the package instantiation.

|configuring_blank_lines_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

     generic map (

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg
     generic map (

package_instantiation_300
#########################

|phase_4| |error| |indent|

Alias: :code:`package_instantiation_indent`

This rule checks the indent of the package declaration.

**Violation**

.. code-block:: vhdl

   library ieee;

     package my_pkg is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   library ieee;

   package my_pkg is new my_generic_pkg

package_instantiation_500
#########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`package_instantiation_package_keyword_case`

This rule checks the **package** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   PACKAGE my_pkg is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_501
#########################

|phase_6| |error| |case| |case_name|

Alias: :code:`package_instantiation_name_case`

This rule checks the instantiated package name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   package MY_PKG is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_502
#########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`package_instantiation_is_keyword_case`

This rule checks the **is** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg IS new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_503
#########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`package_instantiation_new_keyword_case`

This rule checks the **new** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is NEW my_generic_pkg

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_504
#########################

|phase_6| |error| |case| |case_name|

Alias: :code:`package_instantiation_uninstantiated_package_name_case`

This rule checks the uninstantiated package name has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is new MY_GENERIC_PKG

**Fix**

.. code-block:: vhdl

   package my_pkg is new my_generic_pkg

package_instantiation_600
#########################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`package_instantiation_identifier_suffix`

This rule checks for valid suffixes on package identifiers.
The default package suffix is *_pkg*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   package foo is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package foo_pkg is new my_generic_pkg

package_instantiation_601
#########################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`package_instantiation_identifier_prefix`

This rule checks for valid prefixes on instantiated package identifiers.
The default package prefix is *pkg_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   package foo is new my_generic_pkg

**Fix**

.. code-block:: vhdl

   package pkg_foo is new my_generic_pkg
