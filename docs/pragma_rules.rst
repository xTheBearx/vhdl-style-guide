.. include:: includes.rst

Pragma Rules
------------

pragma_100
##########

|phase_2| |disabled| |error| |whitespace|

Alias: :code:`pragma_space_after_dashes`

This rule checks the space after the **--** of a pragma.

.. NOTE:: This rule is disabled by default.

The rule has an :code:`action` option:

* :code:`add` (default): a single space after the **--**
* :code:`remove`: no space after the **--**

A pragma is only changed if the result still matches a pragma pattern of the same kind (open, close or single).
For example, :code:`--vhdl_comp_off` is never changed by the default patterns, because they do not match :code:`-- vhdl_comp_off`.

**Violation**

.. code-block:: vhdl

   --synthesis translate_off
   --   synthesis translate_on

**Fix**

.. code-block:: vhdl

   -- synthesis translate_off
   -- synthesis translate_on

pragma_300
##########

|phase_4| |error| |indent|

Alias: :code:`pragma_indent`

This rule checks the indent of pragmas.

|configuring_pragmas_link|

**Violation**

.. code-block:: vhdl

   architecture rtl of fifo is

   -- synthesis translate_off
     signal wr_en : std_logic;
     signal rd_en : std_Logic;
   -- synthesis translate_on

   begin

**Fix**

.. code-block:: vhdl

   architecture rtl of fifo is

     -- synthesis translate_off
     signal wr_en : std_logic;
     signal rd_en : std_Logic;
     -- synthesis translate_on

   begin

pragma_400
##########

|phase_3| |error| |blank_line|

Alias: :code:`pragma_lines_above_opening_pragma`

This rule checks for blank lines or comments above opening pragmas.

|configuring_previous_line_rules_link|

|configuring_pragmas_link|

The default style is :code:`no_code`.

**Violation**

.. code-block:: vhdl

   end component;
   -- synthesis translate_on

**Fix**

.. code-block:: vhdl

   end component;

   -- synthesis translate_on

pragma_401
##########

|phase_3| |error| |blank_line|

Alias: :code:`pragma_blank_line_below_opening_pragma`

This rule checks for a blank line below opening pragmas.

|configuring_blank_lines_link|

|configuring_pragmas_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

   -- synthesis translate_on

   signal rd_en : std_logic;


**Fix**

.. code-block:: vhdl

   -- synthesis translate_on
   signal rd_en : std_logic;

pragma_402
##########

|phase_3| |error| |blank_line|

Alias: :code:`pragma_lines_above_closing_pragma`

This rule checks for blank lines or comments above closing pragmas.

|configuring_previous_line_rules_link|

|configuring_pragmas_link|

The default style is :code:`no_blank_line`.

**Violation**

.. code-block:: vhdl

   end component;

   -- synthesis translate_off

**Fix**

.. code-block:: vhdl

   end component;
   -- synthesis translate_off

pragma_403
##########

|phase_3| |error| |blank_line|

Alias: :code:`pragma_blank_line_below_closing_pragma`

This rule checks for a blank line below closing pragmas.

|configuring_blank_lines_link|

|configuring_pragmas_link|

The default style is :code:`require_blank_line`.

**Violation**

.. code-block:: vhdl

   -- synthesis translate_off
   signal rd_en : std_logic;


**Fix**

.. code-block:: vhdl

   -- synthesis translate_off

   signal rd_en : std_logic;
