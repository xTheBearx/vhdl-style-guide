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
A loop through a black box is found when the declaration of its type gives the output a path role from the input.
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
A black box ends a path, unless the declaration of its type gives the output a path role: the path then continues through it, with no logic level for the box.
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

design_016
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_reconvergence`

This rule reports signals synchronized separately from one clock domain that meet again.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

Each synchronizer takes one or two cycles of the destination clock, and which one is random.
Two signals that change together in the source domain can therefore arrive in different cycles, and logic that
combines them can see a state the source never had, for example a request without its qualifier.
Two synchronizers of the same signal can disagree for a cycle in the same way.
Every synchronizer tags its output, and the tags follow the signal through logic, registers and memories of the destination domain.
A reconvergence is reported where tags of two synchronizers first meet: at a register, a memory, a black box input or an output.
The inputs a black box declares synchronous to one of its clock pins count as one place, and a declared path through a black box is followed.
Synchronize one signal and derive the others from it in the destination domain, use a handshake, or gray code a counter.
The bits of one bus count as one signal: a gray-coded bus is meant to be combined, and design_009 reports other buses.
A synchronous reset, an input that loads a constant into two or more registers, is a reset path rather than data
and is not followed, unless :code:`follow_resets` is true; the crossing report lists the meetings through resets either way.
A synchronous clear that logic computes, such as a state machine, is data: list it under :code:`clears` in the cdc
section of the design, and it is followed. Structure cannot tell a clear from a reset, as reset crossing circuits
compute their resets with logic too.

**Violation**

.. code-block:: vhdl

   process (clk_b) is
   begin
     if rising_edge(clk_b) then
       start_meta <= start_a;
       start_b    <= start_meta;
       mode_meta  <= mode_a;
       mode_b     <= mode_meta;
       go_b       <= start_b and mode_b;  -- start_a and mode_a meet again
     end if;
   end process;

design_017
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_black_box_declaration`

This rule reports black boxes whose effect on clock domains is not declared.

.. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

Design analysis cannot see inside a black box, such as a vendor primitive, a vendor macro or encrypted IP, and
assumes nothing about one. Each black box type must be declared in the black_boxes part of the design section,
or in a black box library, with a role for every port: which pins are clocks, which data is timed by which clock,
which outputs follow inputs, which clocks it makes, and what it synchronizes inside.
A static port needs a justification and reviewed_by.
:code:`mhsg --design --black_box_template FILE` writes a template of the declarations a design needs.

**Violation**

.. code-block:: vhdl

   -- vendor_dma has no declaration
   u_dma : vendor_dma port map (aclk => clk, irq => irq);

design_018
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_reset_domain_crossing`

This rule reports reset domain crossings: data from a register with one asynchronous reset, directly or through
logic, into a register of the same clock that another asynchronous reset clears.

.. NOTE:: This is a design rule. It runs in design analysis.

Asserting the reset of the source changes its output at any time, so a destination that is not reset with it can
capture the change metastable. The crossing is safe when the destination is reset whenever the source is: when its
reset comes from the same reset, or combines it with others, directly or through reset synchronizers.
Registers without an asynchronous reset are not reported, as their data during a reset is not used, and neither
are the registers of reset synchronizers.

**Violation**

.. code-block:: vhdl

   process (clk, rst_a) is
   begin
     if rst_a = '1' then
       a_r <= '0';
     elsif rising_edge(clk) then
       a_r <= d;
     end if;
   end process;

   process (clk, rst_b) is
   begin
     if rst_b = '1' then
       b_r <= '0';
     elsif rising_edge(clk) then
       b_r <= a_r;
     end if;
   end process;

**Fix**

Reset b_r with rst_a too, for example with a reset that combines both, or keep a_r stable while rst_a is asserted.

design_019
##########

|phase_7| |disabled| |error| |unfixable| |design|

Alias: :code:`design_mapped_logic_depth`

This rule reports the registers and output ports of the design reached by a combinational path of more than
**maximum_levels** levels, 8 by default, after the design is mapped to look-up tables of **lut_size** inputs, 6 by
default: each register once, with its deepest path.

.. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: mapping takes longer than
          the other checks.

design_007 counts the operators of a path before synthesis, which tells where a path is deep but not how deep it
is in the device. This rule flattens the design, maps it with Yosys to look-up tables, and counts the tables on
the paths between registers, memories and the ports of the design, which is closer to the timing of the device.
Mapping keeps the registers but renames the logic between them, so a finding names the register or port a path
starts at, when it has a name, and the register it ends at, and is reported at the assignment of that register.

**Violation**

A chain of comparisons and multiplexers that maps to more look-up tables than allowed between two registers.
