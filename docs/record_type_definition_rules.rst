.. include:: includes.rst

Record Type Definition Rules
----------------------------

record_type_definition_001
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_record_keyword_location`

This rule checks the location of the **record** keyword.

The default location is not on a line by itself.

|configuring_move_token_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is
   record

**Fix**

.. code-block:: vhdl

   type t_record is record

record_type_definition_002
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_no_code_after_record_keyword`

This rule checks for code after the **record** keyword.

**Violation**

.. code-block:: vhdl

   type t_record is record a : std_logic;
     b : std_logic;
   end record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record;

record_type_definition_003
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_end_keyword_on_own_line`

This rule checks the **end** keyword is on its own line.

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic; end record;


**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record;

record_type_definition_004
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_is_keyword_on_same_line_as_record`

This rule checks the **is** keyword is on the same line as the **record** keyword.

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end
   record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record
   ;

record_type_definition_005
##########################

|phase_1| |error| |structure| |structure_optional|

Alias: :code:`record_type_definition_end_simple_name_exists`

This rule checks for the optional simple name in the **end record** statement.

|configuring_optional_items_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_006
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_simple_name_on_same_line_as_record`

This rule checks the optional simple name is on the same line as the **record** keyword.

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record
   t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record
   ;

record_type_definition_007
##########################

|phase_1| |error| |structure|

Alias: :code:`record_type_definition_semicolon_on_same_line_as_record`

This rule checks the semicolon is on the same line as the **record** keyword.

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record
   ;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_100
##########################

|phase_2| |error| |whitespace|

Alias: :code:`record_type_definition_space_after_end_keyword`

This rule checks for a single space after the **end** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end         record t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_101
##########################

|phase_2| |error| |whitespace|

Alias: :code:`record_type_definition_space_before_simple_name`

This rule checks for a single space before the simple name.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record    t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_200
##########################

|phase_3| |error| |blank_line|

Alias: :code:`record_type_definition_blank_line_below_record_keyword`

This rule checks for blank lines below the **record** keyword.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

   type t_record is record

     a : std_logic;
     b : std_logic;
   end record    t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_201
##########################

|phase_3| |error| |blank_line|

Alias: :code:`record_type_definition_blank_line_above_end_keyword`

This rule checks for blank lines above the **end** keyword.

|configuring_previous_line_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;

   end record    t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_300
##########################

|phase_4| |error| |indent|

Alias: :code:`record_type_definition_record_keyword_indent`

This rule checks the indent of the **record** keyword if it is on its own line.

**Violation**

.. code-block:: vhdl

   type t_record is
        record
     a : std_logic;
     b : std_logic;
   end record t_record;

**Fix**

.. code-block:: vhdl

   type t_record is
   record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_301
##########################

|phase_4| |error| |indent|

Alias: :code:`record_type_definition_end_keyword_indent`

This rule checks the indent of the **end** keyword.

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
       end record t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_500
##########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`record_type_definition_record_keyword_case`

This rule checks the proper case of the **record** keyword.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is RECORD
     a : std_logic;
     b : std_logic;
   end record t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_501
##########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`record_type_definition_end_keyword_case`

This rule checks the proper case of the **end** keyword.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   END record t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_502
##########################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`record_type_definition_end_record_keyword_case`

This rule checks the proper case of the end **record** keyword.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end RECORD t_record;

**Fix**

.. code-block:: vhdl

   type t_record is record
     a : std_logic;
     b : std_logic;
   end record t_record;

record_type_definition_503
##########################

|phase_6| |error| |case| |case_name|

Alias: :code:`record_type_definition_element_names_consistent_case`

This rule checks record element names are used with the same capitalization as in the record type declaration.

Element names are checked in selected names, such as **rec.element**, whose prefix is declared in the file,
and in the choices of aggregates, such as **(element => value)**.
Element names declared with different capitalizations in different records, or which also name another declaration, are not checked.

**Violation**

.. code-block:: vhdl

   type t_rec is record
     sl_Valid : std_logic;
   end record t_rec;

   constant c_rec : t_rec := (sl_valid => '0');

   rec.SL_VALID <= '1';

**Fix**

.. code-block:: vhdl

   type t_rec is record
     sl_Valid : std_logic;
   end record t_rec;

   constant c_rec : t_rec := (sl_Valid => '0');

   rec.sl_Valid <= '1';
