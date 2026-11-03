.. include:: includes.rst

Design Rules
------------

design_001
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_ghdl_error`

This rule reports the errors GHDL finds when it analyzes and elaborates the design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 checks CP1 and CP13.

GHDL reports, among others, wrong types, names that are not declared, and ranges that do not match.
Design analysis stops at the first step with errors, so later steps and the other design rules do not run until they are fixed.

**Violation**

.. code-block:: vhdl

   signal tx_index : std_logic_vector(14 downto 0);
   tx_index <= rf2fe_vec;  -- rf2fe_vec is of another type

design_002
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_latch`

This rule reports latches in the synthesized design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS4.

It finds the latches synthesis infers, including those in other files and those lint_009 cannot see,
for example from a case statement on an enumerated type that does not assign a signal in every choice.
The latch is reported at the assignment in the process that infers it.

**Violation**

.. code-block:: vhdl

   process (all) is
   begin
     if en = '1' then
       q <= a;
     end if;
   end process;
