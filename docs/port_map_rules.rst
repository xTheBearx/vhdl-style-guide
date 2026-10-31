.. include:: includes.rst

Port Map Rules
--------------

port_map_001
############

|phase_6| |error| |case| |case_keyword|

Alias: :code:`port_map_keyword_case`

This rule checks the **port map** keywords have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   PORT MAP (

**Fix**

.. code-block:: vhdl

   port map (

port_map_002
############

|phase_6| |error| |case| |case_name|

Alias: :code:`port_map_port_name_case`

This rule checks the port names have proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

     port map (
       wr_en              => wr_en,
       rd_en              => rd_en,
       OVERFLOW           => overflow,
       underflow(c_index) => underflow
     );

**Fix**

.. code-block:: vhdl

     port map (
       wr_en              => wr_en,
       rd_en              => rd_en,
       overflow           => overflow,
       underflow(c_index) => underflow
     );

port_map_003
############

|phase_1| |error| |structure|

Alias: :code:`port_map_open_parenthesis_on_same_line_as_map`

This rule checks the "(" character is on the same line as the **map** keyword.

**Violation**

.. code-block:: vhdl

   port map
   (
     WR_EN    => WR_EN,
     RD_EN    => RD_EN,
     OVERFLOW => OVERFLOW
   );

**Fix**

Use explicit port mapping.

.. code-block:: vhdl

   port map (

     WR_EN    => WR_EN,
     RD_EN    => RD_EN,
     OVERFLOW => OVERFLOW
   );

port_map_004
############

|phase_1| |error| |structure|

Alias: :code:`port_map_closing_parenthesis_location`

This rule checks the location of the closing ")" character for the port map.

The default location is on a line by itself.

|configuring_move_token_rules_link|

**Violation**

.. code-block:: vhdl

    port map (
      WR_EN => wr_en);

**Fix**

.. code-block:: vhdl

    port map (
      WR_EN => wr_en
    );

port_map_005
############

|phase_1| |error| |structure|

Alias: :code:`port_map_no_assignment_on_map_line`

This rule checks for a port assignment on the same line as the **port map** keyword.

**Violation**

.. code-block:: vhdl

     port map (WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

**Fix**

.. code-block:: vhdl

     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

port_map_006
############

|phase_2| |error| |whitespace|

Alias: :code:`port_map_space_before_open_parenthesis`

This rule checks for a single space between the **map** keyword and the (.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   port map(

   port map   (

**Fix**

.. code-block:: vhdl

   port map (

   port map (

port_map_007
############

|phase_2| |error| |whitespace|

Alias: :code:`port_map_space_after_arrow`

This rule checks for a single space after the **=>** operator in port maps.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    =>   wr_en,
       RD_EN    =>rd_en,
       OVERFLOW =>     overflow
     );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

port_map_008
############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`port_map_no_positional_ports`

This rule checks for positional ports.
Positional ports are subject to problems when the position of the underlying component changes.

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

port_map_009
############

|phase_1| |error| |structure|

Alias: :code:`port_map_one_assignment_per_line`

This rule checks multiple port assignments on the same line.

**Violation**

.. code-block:: vhdl

   port map (
     WR_EN => w_wr_en, RD_EN => w_rd_en,
     OVERFLOW => w_overflow
   );

**Fix**

.. code-block:: vhdl

   port map (
     WR_EN => w_wr_en,
     RD_EN => w_rd_en,
     OVERFLOW => w_overflow
   );

port_map_010
############

|phase_1| |error| |structure|

Alias: :code:`port_map_no_comments_at_end_of_assignments`

This rule checks for comments at the end of the port and generic assignments in instantiations.
These comments represent additional maintenance.
They will be out of sync with the entity at some point.
Refer to the entity for port types, port directions and purpose.

**Violation**

.. code-block:: vhdl

   WR_EN => w_wr_en;   -- out : std_logic
   RD_EN => w_rd_en;   -- Reads data when asserted

**Fix**

.. code-block:: vhdl

   WR_EN => w_wr_en;
   RD_EN => w_rd_en;

port_map_011
############

|phase_1| |error| |structure|

Alias: :code:`port_map_map_keyword_on_same_line_as_port`

This rule checks the **map** keyword is on the same line as the **port** keyword.

**Violation**

.. code-block:: vhdl

   port
   map (
     WR_EN    => WR_EN,
     RD_EN    => RD_EN,
     OVERFLOW => OVERFLOW
   );

**Fix**

Use explicit port mapping.

.. code-block:: vhdl

   port map (

     WR_EN    => WR_EN,
     RD_EN    => RD_EN,
     OVERFLOW => OVERFLOW
   );

port_map_012
############

|phase_1| |disabled| |error| |structure|

Alias: :code:`port_map_association_order`

This rule checks the order of the associations in port maps.

.. NOTE:: This rule is disabled by default.

The order is set by these options:

* :code:`order`: :code:`declaration` (default) follows the order of the ports in the entity or component declaration.
  :code:`name` sorts the associations by the name of their formal part.
* :code:`sort_within_sections`: :code:`yes` (default) sorts each group of associations separated by a blank line or comment line on its own.
  :code:`no` sorts the whole port map.

The declaration is looked up in the file and in the other files of the run.
A component instance uses the component declaration, or the entity of the same name if there is none.
Port maps are not checked if the declaration is not known, if it is declared differently in several places, if a formal part is not one of its ports, or if they use positional association.
Associations of the same port, such as :code:`data(0)` and :code:`data(1)`, keep their order.

Moving named associations does not change what the instance connects, so the rule moves them if each association is on a line of its own.
Comments at the end of a line move with their association.
When port_028 moves the ports of an entity in another file, run the fix again so the port maps follow the new order.

**Violation**

.. code-block:: vhdl

   entity sub is
     port (
       clk  : in  std_logic;
       data : out std_logic
     );
   end entity sub;

   u_sub : entity work.sub
     port map (
       data => s_data,
       clk  => clk
     );

**Fix**

.. code-block:: vhdl

   u_sub : entity work.sub
     port map (
       clk  => clk,
       data => s_data
     );

port_map_100
############

|phase_2| |error| |whitespace|

Alias: :code:`port_map_space_before_arrow`

This rules checks for whitespace before the assignment operator.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   port map (
     WR_EN=> w_wr_en,
     RD_EN=> w_rd_en,
     OVERFLOW => w_overflow
   );

**Fix**

.. code-block:: vhdl

   port map (
     WR_EN => w_wr_en,
     RD_EN => w_rd_en,
     OVERFLOW => w_overflow
   );

port_map_101
############

|phase_2| |error| |whitespace|

Alias: :code:`port_map_space_between_port_and_map`

This rule checks for a single space between the **port** keyword and the **map** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   port   map (

**Fix**

.. code-block:: vhdl

   port map (

port_map_200
############

|phase_3| |error| |blank_line|

Alias: :code:`port_map_blank_line_below_open_parenthesis`

This rule checks for a blank line below the open parenthesis in a port map.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

  port map (

    WR_EN => w_wr_en,
    RD_EN => w_rd_en,
    OVERFLOW => w_overflow
  );

**Fix**

.. code-block:: vhdl

  port map (
    WR_EN => w_wr_en,
    RD_EN => w_rd_en,
    OVERFLOW => w_overflow
  );

port_map_201
############

|phase_3| |error| |blank_line|

Alias: :code:`port_map_blank_lines_between_associations`

This rule checks for blank lines in a port map.

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


port_map_202
############

|phase_3| |error| |blank_line|

Alias: :code:`port_map_lines_above_closing_parenthesis`

This rule checks for blank lines or comments above the closing parenthesis in a port map.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

  port map (
    WR_EN => w_wr_en,
    RD_EN => w_rd_en

  );

**Fix**

.. code-block:: vhdl

  port map (
    WR_EN => w_wr_en,
    RD_EN => w_rd_en
  );

port_map_203
############

|phase_3| |error| |blank_line|

Alias: :code:`port_map_lines_above_keyword`

This rule checks for blank lines or comments above the **port map** keywords.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

  U_FIFO : FIFO
    generic map (
      G_WIDTH => 8
    )

    port map (
      WR_EN => w_wr_en
    );

**Fix**

.. code-block:: vhdl

  U_FIFO : FIFO
    generic map (
      G_WIDTH => 8
    )
    port map (
      WR_EN => w_wr_en
    );

port_map_300
############

|phase_4| |error| |indent|

Alias: :code:`port_map_port_keyword_indent`

This rule checks for the proper indentation of the **port** keyword in port maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
       port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

port_map_301
############

|phase_4| |error| |indent|

Alias: :code:`port_map_association_indent`

This rule checks for the proper indentation of association elements in port maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
           WR_EN    => wr_en,
   RD_EN    => rd_en,
         OVERFLOW => overflow
     );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );

port_map_302
############

|phase_4| |error| |indent|

Alias: :code:`port_map_closing_parenthesis_indent`

This rule checks for the proper indentation of the closing parenthesis in port maps.

**Violation**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
          );

**Fix**

.. code-block:: vhdl

   U_FIFO : FIFO
     port map (
       WR_EN    => wr_en,
       RD_EN    => rd_en,
       OVERFLOW => overflow
     );
