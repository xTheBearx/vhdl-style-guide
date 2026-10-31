.. include:: includes.rst

Generic Rules
-------------

generic_001
###########

This rule has been moved to `entity_200 <entity_rules.html#entity-200>`_ to isolate the rule to entity declarations.

generic_002
###########

|phase_4| |error| |indent|

Alias: :code:`generic_keyword_indent`

This rule checks the indent of the **generic** keyword.

**Violation**

.. code-block:: vhdl

   entity fifo is
        generic (

   entity fifo is
   generic (

**Fix**

.. code-block:: vhdl

   entity fifo is
     generic (

   entity fifo is
     generic (

generic_003
###########

|phase_2| |error| |whitespace|

Alias: :code:`generic_space_after_generic_keyword`

This rule checks for a single space between the **generic** keyword and the (.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   generic    (

   generic(

**Fix**

.. code-block:: vhdl

   generic (

   generic (

generic_004
###########

|phase_4| |error| |indent|

Alias: :code:`generic_declarations_indent`

This rule checks the indent of generic declarations.

**Violation**

.. code-block:: vhdl

   generic (
   g_width : integer := 32;
          g_depth : integer := 512
   )

**Fix**

.. code-block:: vhdl

   generic (
     g_width : integer := 32;
     g_depth : integer := 512
   )

generic_005
###########

|phase_2| |error| |whitespace|

Alias: :code:`generic_space_after_colon`

This rule checks for a single space after the colon in a generic declaration.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   g_width :integer := 32;

**Fix**

.. code-block:: vhdl

   g_width : integer := 32;

generic_006
###########

|phase_2| |error| |whitespace|

Alias: :code:`generic_space_after_default_assignment`

This rule checks for a single space after the default assignment.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   g_width : integer :=32;
   g_depth : integer :=     512;

**Fix**

.. code-block:: vhdl

   g_width : integer := 32;
   g_depth : integer := 512;

generic_007
###########

|phase_6| |error| |case| |case_name|

Alias: :code:`generic_name_case`

This rule checks the generic names have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   G_WIDTH : integer := 32;

**Fix**

.. code-block:: vhdl

   g_width : integer := 32;

generic_008
###########

|phase_4| |error| |indent|

Alias: :code:`generic_closing_parenthesis_indent`

This rule checks the indent of the closing parenthesis.

**Violation**

.. code-block:: vhdl

   g_depth : integer := 512
   );

**Fix**

.. code-block:: vhdl

     g_depth : integer := 512
   );

generic_009
###########

|phase_6| |error| |case| |case_keyword|

Alias: :code:`generic_keyword_case`

This rule checks the **generic** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   GENERIC (

**Fix**

.. code-block:: vhdl

   generic (

generic_010
###########

|phase_1| |error| |structure|

Alias: :code:`generic_closing_parenthesis_location`

This rule checks the location of the closing ")" character for the generic clause.

The default location is on a line by itself.

|configuring_move_token_rules_link|

**Violation**

.. code-block:: vhdl

   g_depth : integer := 512);

**Fix**

.. code-block:: vhdl

     g_depth : integer := 512
   );

generic_013
###########

|phase_1| |error| |structure|

Alias: :code:`generic_no_declaration_on_generic_keyword_line`

This rule checks for the **generic** keyword on the same line as a generic declaration.

**Violation**

.. code-block:: vhdl

   generic (g_depth : integer := 512;

**Fix**

.. code-block:: vhdl

   generic (
     g_depth : integer := 512;

generic_014
###########

|phase_2| |error| |whitespace|

Alias: :code:`generic_space_before_colon`

This rule checks for at least a single space before the colon.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   g_address_width: integer := 10;
   g_data_width : integer := 32;
   g_depth: integer := 512;

**Fix**

.. code-block:: vhdl

   g_address_width : integer := 10;
   g_data_width : integer := 32;
   g_depth : integer := 512;

generic_016
###########

|phase_1| |error| |structure|

Alias: :code:`generic_one_generic_per_line`

This rule checks for multiple generics defined on a single line.

**Violation**

.. code-block:: vhdl

  generic (
    g_width : std_logic := '0';g_depth : std_logic := '1'
  );

**Fix**

.. code-block:: vhdl

  generic (
    g_width : std_logic := '0';
    g_depth : std_logic := '1'
  );

generic_017
###########

This rule was deprecated and replaced with the following rule:

* :ref:`type_mark_500`

generic_018
###########

|phase_1| |error| |structure|

Alias: :code:`generic_open_parenthesis_on_same_line_as_keyword`

This rule checks the **generic** keyword is on the same line as the (.

**Violation**

.. code-block:: vhdl

  generic
   (

**Fix**

.. code-block:: vhdl

  generic (

generic_019
###########

|phase_3| |error| |blank_line|

Alias: :code:`generic_no_blank_lines_before_closing_parenthesis`

This rule checks for blank lines before the ); of the generic declaration.

**Violation**

.. code-block:: vhdl

  generic (
    g_width : std_logic := '0';
    g_depth : Std_logic := '1'


  );

**Fix**

.. code-block:: vhdl

  generic (
    g_width : std_logic := '0';
    g_depth : Std_logic := '1'
  );

generic_020
###########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`generic_prefix`

This rule checks for valid prefixes on generic identifiers.
The default generic prefix is *g_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic(my_generic : integer);

**Fix**

.. code-block:: vhdl

   generic(g_my_generic : integer);

generic_021
###########

|phase_1| |error| |structure|

Alias: :code:`generic_semicolon_not_on_own_line`

This rule checks the semicolon is not on its own line.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic (
       G_WIDTH : integer
     )
     ;

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic (
       G_WIDTH : integer
     );

generic_022
###########

|phase_1| |disabled| |error| |structure|

Alias: :code:`generic_alphabetical_order`

This rule checks generics are declared in alphabetical order.

A generic may use generics declared before it, for example in its default value.
Such a generic is expected after the generics it uses, so the expected order is alphabetical wherever the dependencies allow.
Names are compared ignoring case.

With the :code:`sort_within_sections` option set to :code:`yes` (default), each group of generics separated by a blank line or comment line is sorted on its own.
:code:`no` sorts the whole generic list.

.. NOTE:: This rule is disabled by default.

By default the rule only reports the expected order.
Moving the generics of an entity changes what a direct instantiation with positional generic association connects to.
With :code:`move_generics` set to :code:`when_safe`, the generics of an entity are moved if no file of the run instantiates it directly with a positional generic association.
Instances in files that are not part of the run are not checked, and input from stdin is never moved.
Generics of components, packages and subprograms are only reported.
Generics are only moved if each declaration is on a line of its own; comments at the end of a line move with their generic.

**Violation**

.. code-block:: vhdl

   generic (
     G_WIDTH : integer := 8;
     G_DEPTH : integer := 16;
     G_ADDR_WIDTH : integer := G_DEPTH / 4
   );

**Fix**

.. code-block:: vhdl

   generic (
     G_DEPTH : integer := 16;
     G_ADDR_WIDTH : integer := G_DEPTH / 4;
     G_WIDTH : integer := 8
   );

generic_023
###########

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`generic_section_comment`

This rule checks each group of generics has a section comment above it.

.. NOTE:: This rule is disabled by default.

A group of generics is separated from the next group by a blank line or a comment line.
At least one of the comment lines directly above the first generic of each group must match the :code:`section_pattern` option, a regular expression.
The default pattern accepts any comment.
For example, :code:`'^-- [A-Z]'` requires a comment starting with a capital letter.

This rule only reports groups without a section comment, because it cannot know their names.
generic_022 checks the order of the generics within each section.

**Violation**

.. code-block:: vhdl

   generic (
     G_ADDR_WIDTH : integer := 8;
     G_DATA_WIDTH : integer := 32;

     G_DEBUG : boolean := false
   );

**Fix**

.. code-block:: vhdl

   generic (
     -- Bus widths
     G_ADDR_WIDTH : integer := 8;
     G_DATA_WIDTH : integer := 32;

     -- Simulation
     G_DEBUG : boolean := false
   );

generic_600
###########

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`generic_suffix`

This rule checks for valid suffixes on generic identifiers.
The default generic suffix is *_g*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic(my_generic : integer);

**Fix**

.. code-block:: vhdl

   generic(my_generic_g : integer);
