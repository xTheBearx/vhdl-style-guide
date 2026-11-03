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

design_008
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_unsynchronized_crossing`

This rule reports signals that cross from one clock domain to another without a synchronizer.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

A register that captures a signal from an asynchronous clock domain can go metastable.
A single-bit crossing needs a synchronizer: two or more registers in series in the destination domain, the first fed directly from a register of the source domain and feeding only the next.
Data captured while an enable synchronized to the destination clock holds it, as in a handshake, is safe.
Clocks are asynchronous unless the design section groups them, see the design analysis documentation, where crossings can also be waived with a justification.
A waiver without a justification is reported by this rule.

**Violation**

.. code-block:: vhdl

   process (clk_b) is
   begin
     if rising_edge(clk_b) then
       flag_b <= flag_a;  -- flag_a is clocked by clk_a
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (clk_b) is
   begin
     if rising_edge(clk_b) then
       flag_meta <= flag_a;
       flag_b    <= flag_meta;
     end if;
   end process;

design_009
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_crossing_hazard`

This rule reports clock domain crossings with a synchronizer that can still fail.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

Two hazards are reported:

* logic between the clock domains before the first synchronizer stage, which can glitch and be captured;
* the bits of a bus synchronized one by one, which can arrive in different clock cycles, unless the bus is gray coded.

**Violation**

.. code-block:: vhdl

   sync_meta <= valid_a and ready_a;  -- logic on signals of clock domain a, captured by clk_b
   sync_b    <= sync_meta;

design_010
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_clock_as_data`

This rule reports clocks used as data.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS8.

A clock from an input port or a black box, such as a PLL, should only reach clock pins.
Using it in logic or sampling it with a register makes the design depend on the timing of the clock network.
Logic that gates a clock is reported by design_012 instead.

**Violation**

.. code-block:: vhdl

   process (clk_a) is
   begin
     if rising_edge(clk_a) then
       sample <= clk_b;
     end if;
   end process;

design_011
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_shared_clock_reset`

This rule reports signals used both as a clock and as an asynchronous reset.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS9.

**Violation**

.. code-block:: vhdl

   process (clk_a, clk_c) is
   begin
     if clk_c = '1' then
       q <= '0';
     elsif rising_edge(clk_a) then
       q <= d;
     end if;
   end process;

design_012
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_gated_clock`

This rule reports gated clocks: clocks that pass through logic.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS10.

Logic on a clock adds skew and can glitch, which clocks registers when they should not be.
Use a clock enable instead, or a clock gating cell of the device.
Registers on a gated clock are in the clock domain of the clock that is gated.

**Violation**

.. code-block:: vhdl

   clk_gated <= clk and enable;

design_013
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_generated_clock`

This rule reports clocks made inside the design by a register, such as a clock divider, or by logic.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS11.

A clock from a register or logic is not on the clock network of the device, so it has more skew, and timing analysis needs it to be declared.
Use a clock enable in the domain of the original clock, or a clock management block of the device.
Registers on a divided clock are in the clock domain of the clock that is divided.

**Violation**

.. code-block:: vhdl

   div <= not div when rising_edge(clk);

   process (div) is
   begin
     if rising_edge(div) then
       q <= d;
     end if;
   end process;

design_014
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_generated_reset`

This rule reports asynchronous resets made inside the design by logic or by a register that is not a reset synchronizer.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS12.

Logic on an asynchronous reset can glitch and reset registers when it should not.
The output of a reset synchronizer, a chain of registers that the reset clears and that load a constant, is not reported.

**Violation**

.. code-block:: vhdl

   process (clk, soft_reset, reset) is
   begin
     if (soft_reset or reset) = '1' then
       q <= '0';
     elsif rising_edge(clk) then
       q <= d;
     end if;
   end process;

design_015
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_reset_release`

This rule reports asynchronous resets that are not released synchronously to the clock of the registers they reset.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS15.

A reset may be asserted asynchronously, but released close to a clock edge it leaves registers in different states.
Release it through a reset synchronizer in each clock domain: a chain of two or more registers that the reset clears and that load a constant.
Two cases are reported: a reset input that resets registers directly, and a reset synchronized to one clock that resets registers of another.
A reset input declared in the domain of the registers under inputs in the cdc section is taken as synchronous.

**Violation**

.. code-block:: vhdl

   process (clk, reset) is
   begin
     if reset = '1' then
       q <= '0';
     elsif rising_edge(clk) then
       q <= d;
     end if;
   end process;
