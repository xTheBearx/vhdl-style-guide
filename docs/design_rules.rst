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
A generic of the top entity without a default value must be set in the design section, since GHDL would otherwise use the leftmost value of its type.
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

design_003
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_combinational_loop`

This rule reports combinational loops in the synthesized design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS3.

A combinational loop feeds the output of logic back to its input without a register in between.
Unlike lint_008, which checks one process, it finds loops through several processes, concurrent statements and instances of other entities.
Latches, which design_002 reports, are not reported again.

**Violation**

.. code-block:: vhdl

   a <= b and c;
   b <= a or d;

design_004
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_multiple_drivers`

This rule reports signals with more than one driver in the synthesized design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS6.

GHDL reports two processes that drive the same signal as an error, see design_001.
This rule finds the drivers GHDL accepts, such as two instances whose outputs are connected to the same signal.
Tri-state drivers, which assign :code:`'Z'`, are not reported, and neither is an inout port with one driver inside the entity.

**Violation**

.. code-block:: vhdl

   u_a : entity work.source port map (data => bus_data);
   u_b : entity work.source port map (data => bus_data);

design_005
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_constant_register`

This rule reports registers that never change in the synthesized design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS18.

A register is reported when every bit can only ever hold one value: it is assigned only a constant equal to its reset value,
or only keeps its value.
Such a register cannot be controlled, so the logic it feeds cannot be tested, and synthesis removes it.
Registers that are constant only for the generics of this run are reported too: check each configuration that matters.

**Violation**

.. code-block:: vhdl

   process (clk, rst) is
   begin
     if rst = '1' then
       busy <= '0';
     elsif rising_edge(clk) then
       busy <= '0';
     end if;
   end process;

design_006
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_unused_logic`

This rule reports registers that are never used, and signals that are read but never assigned, in the elaborated design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS17.

A register is unused when its value reaches no output of the entity, no instance that uses it, and no memory that is read,
so the register and the logic that feeds only it are unused.
Each entity is checked on its own, so an output that the instantiating entity leaves unconnected does not make the logic behind it unused;
lint_004 reports such outputs.
Unused combinational signals are not reported, since synthesis rewrites them; the registers they feed are.
GHDL removes a register that nothing reads, so a signal that a clocked process assigns but that is missing from the netlist is reported too.
A signal that is read but never assigned is reported at its declaration.

**Violation**

.. code-block:: vhdl

   process (clk) is
   begin
     if rising_edge(clk) then
       count <= count + 1;  -- count is not read anywhere
     end if;
   end process;

design_007
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_logic_depth`

This rule reports combinational paths with more logic levels than :code:`maximum_depth` in the synthesized design.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS19.

A path starts at a register, a memory or an input of the design, and ends at a register, a memory or an output of the design.
Paths through instances of other entities are counted in full, and each path is reported once: in the entity that holds the deepest part.
The depth counts the operators before synthesis maps them to the device: an adder, a comparison or a multiplexer is one level,
inverters count nothing, and a chain of the same and, or or xor operator counts once.
Long chains of if and elsif branches, and loops unrolled into chains of multiplexers, are the usual causes.
Each register is reported once, with its deepest path.

**Violation**

.. code-block:: vhdl

   -- With maximum_depth set to 2
   result <= (a + b) + (c + d) when sel = '1' else (others => '0');
