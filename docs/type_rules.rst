.. include:: includes.rst

Type Rules
----------

type_001
########

|phase_4| |error| |indent|

Alias: :code:`type_indent`

This rule checks the indent of the **type** declaration.

**Violation**

.. code-block:: vhdl

   architecture rtl of fifo is

       type state_machine is (idle, write, read, done);

   begin

**Fix**

.. code-block:: vhdl

   architecture rtl of fifo is

     type state_machine is (idle, write, read, done);

   begin

type_002
########

|phase_6| |error| |case| |case_keyword|

Alias: :code:`type_keyword_case`

This rule checks the **type** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   TYPE state_machine is (idle, write, read, done);

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

type_003
########

This rule was deprecated and replaced with rules:

* `function_015 <function_rules.html#function-015>`_
* `package_019 <package_rules.html#package-019>`_
* `procedure_010 <procedure_rules.html#procedure-010>`_
* `architecture_029 <architecture_rules.html#architecture-029>`_

type_004
########

|phase_6| |error| |case| |case_name|

Alias: :code:`type_identifier_case`

This rule checks the type identifier has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type STATE_MACHINE is (idle, write, read, done);

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

type_005
########

|phase_4| |error| |indent|

Alias: :code:`type_multiline_enumeration_indent`

This rule checks the indent of multiline enumerated types.

**Violation**

.. code-block:: vhdl

   type state_machine is (
   idle,
     write,
   read,
      done);

**Fix**

.. code-block:: vhdl

   type state_machine is (
     idle,
     write,
     read,
     done);

type_006
########

|phase_2| |error| |whitespace|

Alias: :code:`type_space_before_is_keyword`

This rule checks for a single space before the **is** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type state_machine    is (idle, write, read, done);

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

type_007
########

|phase_2| |error| |whitespace|

Alias: :code:`type_space_after_is_keyword`

This rule checks for a single space after the **is** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type state_machine is     (idle, write, read, done);

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

type_008
########

|phase_1| |error| |structure|

Alias: :code:`type_enumeration_closing_parenthesis_on_own_line`

This rule checks the closing parenthesis of multiline enumerated types is on its own line.

**Violation**

.. code-block:: vhdl

   type state_machine is (
     idle,
     write,
     read,
     done);

**Fix**

.. code-block:: vhdl

   type state_machine is (
     idle,
     write,
     read,
     done
   );

type_009
########

|phase_1| |error| |structure|

Alias: :code:`type_enumeration_literal_after_open_parenthesis`

This rule checks for an enumerate type after the open parenthesis on multiline enumerated types.

**Violation**

.. code-block:: vhdl

   type state_machine is (idle,
     write,
     read,
     done
   );

**Fix**

.. code-block:: vhdl

   type state_machine is (
     idle,
     write,
     read,
     done
   );

type_010
########

|phase_3| |error| |blank_line|

Alias: :code:`type_lines_above`

This rule checks for blank lines or comments above the **type** declaration.

|configuring_previous_line_rules_link|

**Violation**

.. code-block:: vhdl

   signal wr_en : std_logic;
   type state_machine is (idle, write, read, done);

**Fix**

.. code-block:: vhdl

   signal wr_en : std_logic;

   type state_machine is (idle, write, read, done);

type_011
########

|phase_3| |error| |blank_line|

Alias: :code:`type_blank_line_below`

This rule checks for a blank line below the **type** declaration.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);
   signal sm : state_machine;

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

   signal sm : state_machine;

type_012
########

|phase_4| |error| |indent|

Alias: :code:`type_record_element_indent`

This rule checks the indent of record elements in record type declarations.

**Violation**

.. code-block:: vhdl

   type interface is record
     data : std_logic_vector(31 downto 0);
   chip_select : std_logic;
       wr_en : std_logic;
   end record;

**Fix**

.. code-block:: vhdl

   type interface is record
     data : std_logic_vector(31 downto 0);
     chip_select : std_logic;
     wr_en : std_logic;
   end record;

type_013
########

|phase_6| |error| |case| |case_keyword|

Alias: :code:`type_is_keyword_case`

This rule checks the **is** keyword in type definitions has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type interface IS record
   type interface Is record
   type interface is record

**Fix**

.. code-block:: vhdl

   type interface is record
   type interface is record
   type interface is record

type_014
########

|phase_6| |error| |case|

Alias: :code:`type_names_consistent_case`

This rule checks for consistent capitalization of type names.

**Violation**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

   signal sm : State_Machine;

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

   signal sm : state_machine;

type_015
########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`type_prefix`

This rule checks for valid prefixes in user defined type identifiers.
The default new type prefix is *t_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   type my_type is range -5 to 5 ;

**Fix**

.. code-block:: vhdl

   type t_my_type is range -5 to 5 ;

type_016
########

|phase_4| |error| |indent|

Alias: :code:`type_closing_parenthesis_indent`

This rule checks the indent of the closing parenthesis on multiline types.

**Violation**

.. code-block:: vhdl

   architecture rtl of fifo is

     type state_machine is (
       idle, write, read, done
       );

   begin

**Fix**

.. code-block:: vhdl

   architecture rtl of fifo is

     type state_machine is (
       idle, write, read, done
     );

   begin

type_017
########

|phase_1| |error| |structure|

Alias: :code:`type_identifier_on_same_line_as_type_keyword`

This rule checks the identifier is on the same line as the **type** keyword.

**Violation**

.. code-block:: vhdl

   type
   t_record is

**Fix**

.. code-block:: vhdl

   type t_record
   is

type_018
########

|phase_1| |error| |structure|

Alias: :code:`type_is_keyword_on_same_line_as_identifier`

This rule checks the **is** keyword is on the same line as the identifier.

**Violation**

.. code-block:: vhdl

   type t_record
   is

**Fix**

.. code-block:: vhdl

   type t_record is

type_100
########

|phase_2| |disabled| |error| |whitespace|

Alias: :code:`type_space_before_identifier`

This rule checks for a single space before the identifier.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type          t_my_type is range -5 to 5;

**Fix**

.. code-block:: vhdl

   type t_my_type is range -5 to 5;

type_200
########

|phase_3| |disabled| |error| |blank_line|

Alias: :code:`type_blank_line_below_unless_followed_by_type`

This rule checks for a blank line below a type declaration unless there is another type declaration.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

   type state_machine_t is (idle, write, read, done);
   type state_machine is (idle, write, read, done);
   constant width : integer := 32;

**Fix**

.. code-block:: vhdl

   type state_machine_t is (idle, write, read, done);
   type state_machine is (idle, write, read, done);

   constant width : integer := 32;

type_400
########

|phase_5| |error| |alignment|

Alias: :code:`type_record_element_colon_alignment`

This rule checks the colons are in the same column for all elements in the block declarative part.

|configuring_keyword_alignment_rules_link|

**Violation**

.. code-block:: vhdl

   type t_some_record is record
     element_1 : natural;
     some_other_element : natural;
     yet_another_element : natural;
   end record;

**Fix**

.. code-block:: vhdl

   type t_some_record is record
     element_1           : natural;
     some_other_element  : natural;
     yet_another_element : natural;
   end record;

type_500
########

|phase_6| |error| |case| |case_name|

Alias: :code:`type_enumeration_literal_case`

This rule checks enumerate types have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type state_machine is (IDLE, WRITE, READ, DONE);

**Fix**

.. code-block:: vhdl

   type state_machine is (idle, write, read, done);

type_501
########

|phase_6| |error| |case|

Alias: :code:`type_enumeration_literal_consistent_case`

This rule checks for consistent capitalization of enumerated types.

**Violation**

.. code-block:: vhdl

   type state is (IDLE, WRITE, READ);

   state <= Idle;
   state <= write;
   state <= ReAd;

**Fix**

.. code-block:: vhdl

   type state is (IDLE, WRITE, READ);

   state <= IDLE;
   state <= WRITE;
   state <= READ;

type_600
########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`type_suffix`

This rule checks for valid suffixes in user defined type identifiers.
The default new type suffix is *_t*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   type my_type is range -5 to 5 ;

**Fix**

.. code-block:: vhdl

   type my_type_t is range -5 to 5 ;

type_601
########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`type_package_prefix`

This rule checks for valid prefixes on type identifiers declared in packages and package bodies.
Types declared inside subprograms are not checked by this rule.
The default prefix is *t_*.

When this rule is enabled, rule type_015 no longer checks types declared in packages, so packages and other code can use different prefixes.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is

     type state is (idle, run);

   end package my_pkg;

**Fix**

With :code:`prefixes = ['pt_']`:

.. code-block:: vhdl

   package my_pkg is

     type pt_state is (idle, run);

   end package my_pkg;

type_602
########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`type_package_suffix`

This rule checks for valid suffixes on type identifiers declared in packages and package bodies.
Types declared inside subprograms are not checked by this rule.
The default suffix is *_t*.

When this rule is enabled, rule type_600 no longer checks types declared in packages, so packages and other code can use different suffixes.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   package my_pkg is

     type state is (idle, run);

   end package my_pkg;

**Fix**

With :code:`suffixes = ['_pt']`:

.. code-block:: vhdl

   package my_pkg is

     type state_pt is (idle, run);

   end package my_pkg;
