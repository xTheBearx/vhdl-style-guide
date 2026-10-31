.. include:: includes.rst

Alias Declaration Rules
-----------------------

alias_declaration_001
#####################

|phase_1| |error| |structure|

Alias: :code:`alias_declaration_alias_keyword_on_own_line`

This rule checks the **alias** keyword is on its own line.

**Violation**

.. code-block:: vhdl

   signal sig1 : std_logic; alias designator is name;

**Fix**

.. code-block:: vhdl

   signal sig1 : std_logic;
   alias designator is name;

alias_declaration_100
#####################

|phase_2| |error| |whitespace|

Alias: :code:`alias_declaration_space_after_colon_subtype_indication`

This rule checks for a single space after the colon for the subtype_indication.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   alias alias_designator :    subtype_indication is name;
   alias alias_designator :subtype_indication is name;

**Fix**

.. code-block:: vhdl

   alias alias_designator : subtype_indication is name;
   alias alias_designator : subtype_indication is name;

alias_declaration_101
#####################

|phase_2| |error| |whitespace|

Alias: :code:`alias_declaration_space_before_is_keyword`

This rule checks for a single space before the **is** keyword if the : is present.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   alias alias_designator : subtype_indication     is name;
   alias alias_designator   is name;

**Fix**

.. code-block:: vhdl

   alias alias_designator : subtype_indication is name;
   alias alias_designator   is name;

alias_declaration_102
#####################

|phase_2| |error| |whitespace|

Alias: :code:`alias_declaration_space_after_is_keyword`

This rule checks for a single space after the **is** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   alias alias_designator is     name;

**Fix**

.. code-block:: vhdl

   alias alias_designator is name;

alias_declaration_103
#####################

|phase_2| |disabled| |error| |whitespace|

Alias: :code:`alias_declaration_space_before_designator`

This rule checks for a single space before the designator.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   alias          alias_designator is name;

**Fix**

.. code-block:: vhdl

   alias alias_designator is name;

alias_declaration_300
#####################

|phase_4| |error| |indent|

Alias: :code:`alias_declaration_alias_keyword_indent`

This rule checks the indent of the **alias** keyword.

**Violation**

.. code-block:: vhdl

   signal sig1 : integer;

     alias is name;

**Fix**

.. code-block:: vhdl

   signal sig1 : integer;

   alias is name;

alias_declaration_500
#####################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`alias_declaration_alias_keyword_case`

This rule checks the **alias** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   ALIAS alias_designator is name;

**Fix**

.. code-block:: vhdl

   alias alias_designator is name;

alias_declaration_501
#####################

|phase_6| |error| |case| |case_keyword|

Alias: :code:`alias_declaration_is_keyword_case`

This rule checks the **is** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   alias alias_designator IS name;

**Fix**

.. code-block:: vhdl

   alias alias_designator is name;

alias_declaration_502
#####################

|phase_6| |error| |case| |case_name|

Alias: :code:`alias_declaration_alias_designator_case`

This rule checks the alias designator has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   alias Alias_Designator is name;

**Fix**

.. code-block:: vhdl

   alias alias_designator is name;

alias_declaration_503
#####################

|phase_6| |error| |case|

Alias: :code:`alias_declaration_alias_designators_consistent_case`

This rule checks for consistent capitalization of alias designators.

**Violation**

.. code-block:: vhdl

   architecture RTL of ENTITY1 is

     signal instructure : bit_vector(15 downto 0);
     alias opcode : bit_vector(3 downto 0) is instructure(15 downto 12);

     signal data : std_logic_vector(OPCODE'range);

   begin

     data <= OpCode;

     PROC_NAME : process () is
     begin

       data <= OpCOde;

       if (opCODE = "0110") then
         data <= oPCode;
       end if;

     end process PROC_NAME;

   end architecture RTL;

**Fix**

.. code-block:: vhdl

   architecture RTL of ENTITY1 is

     signal instructure : bit_vector(15 downto 0);
     alias opcode : bit_vector(3 downto 0) is instructure(15 downto 12);

     signal data : std_logic_vector(opcode'range);

   begin

     data <= opcode;

     PROC_NAME : process () is
     begin

       data <= opcode;

       if (opcode = "0110") then
         data <= opcode;
       end if;

     end process PROC_NAME;

   end architecture RTL;

alias_declaration_600
#####################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`alias_declaration_alias_designators_prefix`

This rule checks for valid prefixes on alias designators.

Default prefix is *a_*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   alias header is name;
   alias footer is name;

**Fix**

.. code-block:: vhdl

   alias a_header is name;
   alias a_footer is name;

alias_declaration_601
#####################

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`alias_declaration_alias_designators_suffix`

This rule checks for valid suffixes on alias designators.

Default prefix is *_a*.

|configuring_prefix_and_suffix_rules_link|

**Violation**

.. code-block:: vhdl

   alias header is name;
   alias footer is name;

**Fix**

.. code-block:: vhdl

   alias header_a is name;
   alias footer_a is name;
