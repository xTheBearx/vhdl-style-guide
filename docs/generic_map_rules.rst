.. include:: includes.rst

Generic Map Rules
-----------------

generic_map_001
###############

|phase_6| |error| |case| |case_keyword|

Alias: :code:`generic_map_keyword_case`

This rule checks the **generic map** keywords have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   GENERIC MAP (

**Fix**

.. code-block:: vhdl

   generic map (

generic_map_002
###############

|phase_6| |error| |case| |case_name|

Alias: :code:`generic_map_generic_name_case`

This rule checks generic names have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

     generic map (
       DEPTH => 512,
       WIDTH => 32
     )

**Fix**

.. code-block:: vhdl

     generic map (
       depth => 512,
       width => 32
     )

generic_map_003
###############

|phase_1| |error| |structure|

Alias: :code:`generic_map_open_parenthesis_on_same_line_as_map`

This rule checks the ( is on the same line as the **map** keyword.

**Violation**

.. code-block:: vhdl

   generic map
   (
     WIDTH => 32,
     DEPTH => 512
   )

**Fix**

Use explicit port mapping.

.. code-block:: vhdl

   generic map (
     WIDTH => 32,
     DEPTH => 512
   )

generic_map_004
###############

|phase_1| |error| |structure|

Alias: :code:`generic_map_closing_parenthesis_location`

This rule checks the location of the closing ")" character for the generic map.

The default location is on a line by itself.

|configuring_move_token_rules_link|

**Violation**

.. code-block:: vhdl

     generic map (
       GENERIC_1 => 0,
       GENERIC_2 => TRUE,
       GENERIC_3 => FALSE)

**Fix**

.. code-block:: vhdl

     generic map (
       GENERIC_1 => 0,
       GENERIC_2 => TRUE,
       GENERIC_3 => FALSE
     )

generic_map_005
###############

|phase_1| |error| |structure|

Alias: :code:`generic_map_no_assignment_on_map_line`

This rule checks if the **generic map** keywords and a generic assignment are on the same line.

**Violation**

.. code-block:: vhdl

     generic map (DEPTH => 512,
       WIDTH => 32
     )

**Fix**

.. code-block:: vhdl

     generic map (
       DEPTH => 512,
       WIDTH => 32
     )

generic_map_006
###############

|phase_2| |error| |whitespace|

Alias: :code:`generic_map_space_before_open_parenthesis`

This rule checks for a single space between the **map** keyword and the (.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   generic map(

   generic map   (

**Fix**

.. code-block:: vhdl

   generic map (

   generic map (

generic_map_007
###############

|phase_2| |error| |whitespace|

Alias: :code:`generic_map_space_after_arrow`

This rule checks for a single space after the **=>** keyword in generic maps.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   generic map
   (
     WIDTH =>    32,
     DEPTH => 512
   )

**Fix**

.. code-block:: vhdl

   generic map
   (
     WIDTH => 32,
     DEPTH => 512
   )

generic_map_008
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`generic_map_no_positional_generics`

This rule checks for positional generics.
Positional ports and generics are subject to problems when the position of the underlying component changes.

**Violation**

.. code-block:: vhdl

   port map (
     WR_EN, RD_EN, OVERFLOW
   );

**Fix**

Use explicit port mapping.

.. code-block:: vhdl

   port map (
     WR_EN    => WR_EN,
     RD_EN    => RD_EN,
     OVERFLOW => OVERFLOW
   );

generic_map_009
###############

|phase_1| |error| |structure|

Alias: :code:`generic_map_map_keyword_on_same_line_as_generic`

This rule checks the **map** keyword is on the same line as the **generic** keyword.

**Violation**

.. code-block:: vhdl

   generic
   map (
     WIDTH => 32,
     DEPTH => 512
   )

**Fix**

Use explicit port mapping.

.. code-block:: vhdl

   generic map (

     WIDTH => 32,
     DEPTH => 512
   )

generic_map_010
###############

|phase_1| |disabled| |error| |structure|

Alias: :code:`generic_map_one_assignment_per_line`

This rule checks multiple generic assignments on the same line.

.. NOTE:: This rule is disabled by default, because short generic maps such as :code:`generic map (A => 1, B => 2)` are common.
   It can be enabled to match port_map_009.

**Violation**

.. code-block:: vhdl

   generic map (
     G_WIDTH => 8, G_DEPTH => 16,
     G_RESET => '0'
   )

**Fix**

.. code-block:: vhdl

   generic map (
     G_WIDTH => 8,
     G_DEPTH => 16,
     G_RESET => '0'
   )

generic_map_100
###############

|phase_2| |error| |whitespace|

Alias: :code:`generic_map_space_before_arrow`

This rules checks for whitespace before the assignment operator.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   generic map (
     WIDTH=> 32,
     DEPTH=> 512
   );

**Fix**

.. code-block:: vhdl

   generic map (
     WIDTH => 32,
     DEPTH => 512
   );

generic_map_101
###############

|phase_2| |error| |whitespace|

Alias: :code:`generic_map_space_between_generic_and_map`

This rule checks for a single space between the **generic** keyword and the **map** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   generic       map(

**Fix**

.. code-block:: vhdl

   generic map (

generic_map_200
###############

|phase_3| |error| |blank_line|

Alias: :code:`generic_map_blank_line_below_open_parenthesis`

This rule checks for a blank line below the open parenthesis in a generic map.

|configuring_blank_lines_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

  generic map (

    G_WIDTH => 8,
    G_DEPTH => 16
  )

**Fix**

.. code-block:: vhdl

  generic map (
    G_WIDTH => 8,
    G_DEPTH => 16
  )

generic_map_201
###############

|phase_3| |error| |blank_line|

Alias: :code:`generic_map_blank_lines_between_associations`

This rule checks for blank lines in a generic map.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

  generic map (
    G_GEN_1 => 3,
    G_GEN_2 => 4,

    G_GEN_3 => 5
  )
  port map (
    PORT_1 => w_port_1,
    PORT_2 => w_port_2,
    PORT_3 => w_port_3
  );

**Fix**

.. code-block:: vhdl

  generic map (
    G_GEN_1 => 3,
    G_GEN_2 => 4,
    G_GEN_3 => 5
  )
  port map (
    PORT_1 => w_port_1,
    PORT_2 => w_port_2,
    PORT_3 => w_port_3
  );

generic_map_202
###############

|phase_3| |error| |blank_line|

Alias: :code:`generic_map_lines_above_closing_parenthesis`

This rule checks for blank lines or comments above the closing parenthesis in a generic map.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

  generic map (
    G_WIDTH => 8,
    G_DEPTH => 16

  )

**Fix**

.. code-block:: vhdl

  generic map (
    G_WIDTH => 8,
    G_DEPTH => 16
  )

generic_map_203
###############

|phase_3| |error| |blank_line|

Alias: :code:`generic_map_lines_above_keyword`

This rule checks for blank lines or comments above the **generic map** keywords.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

  U_FIFO : FIFO

    generic map (
      G_WIDTH => 8
    )

**Fix**

.. code-block:: vhdl

  U_FIFO : FIFO
    generic map (
      G_WIDTH => 8
    )

generic_map_300
###############

|phase_4| |error| |indent|

Alias: :code:`generic_map_generic_keyword_indent`

This rule checks for the proper indentation of the **generic** keyword in generic maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
       generic map (
       G_GEN1 => g_gen1,
       G_GEN2 => g_gen2,
       G_GEN3 => g_gen3
     );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic map (
       G_GEN1 => g_gen1,
       G_GEN2 => g_gen2,
       G_GEN3 => g_gen3
     );

generic_map_301
###############

|phase_4| |error| |indent|

Alias: :code:`generic_map_association_indent`

This rule checks for the proper indentation of association elements in generic maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic map (
           G_GEN1 => g_gen1,
   G_GEN2 => g_gen2,
         G_GEN3 => g_gen3
     );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic map (
       G_GEN1 => g_gen1,
       G_GEN2 => g_gen2,
       G_GEN3 => g_gen3
     );

generic_map_302
###############

|phase_4| |error| |indent|

Alias: :code:`generic_map_closing_parenthesis_indent`

This rule checks for the proper indentation of the closing parenthesis in generic maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic map (
       G_GEN1 => g_gen1,
       G_GEN2 => g_gen2,
       G_GEN3 => g_gen3
          );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     generic map (
       G_GEN1 => g_gen1,
       G_GEN2 => g_gen2,
       G_GEN3 => g_gen3
     );

generic_map_600
###############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`generic_map_generic_name_suffix`

This rule checks for valid suffixes on generic identifiers in generic maps
The default generic suffix is *_g*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic map
   (
     WIDTH => 32,
     DEPTH => 512
   )

**Fix**

.. code-block:: vhdl

   generic map
   (
     WIDTH_G => 32,
     DEPTH_G => 512
   )

generic_map_601
###############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`generic_map_generic_name_prefix`

This rule checks for valid prefixes on generic identifiers in generic maps
The default generic suffix is *g_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   generic map
   (
     WIDTH => 32,
     DEPTH => 512
   )

**Fix**

.. code-block:: vhdl

   generic map
   (
     G_WIDTH => 32,
     G_DEPTH => 512
   )
