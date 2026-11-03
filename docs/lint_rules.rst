.. include:: includes.rst

Lint Rules
----------

lint_001
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_duplicate_signal_assignment`

This rule checks that a signal is assigned at most once in the same statement region of a process.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP2.

A second assignment in the same sequence of statements overrides the first, which is usually a mistake.
An assignment in a nested if or case statement, such as one that overrides a default value, is not a duplicate.
Neither is an assignment after a wait statement or a procedure call, since time can pass there.

**Violation**

.. code-block:: vhdl

   if reset = '1' then
     beep <= '0';
     beep <= '1';
   end if;

**Fix**

.. code-block:: vhdl

   if reset = '1' then
     beep <= '0';
   end if;

lint_002
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_sensitivity_list`

This rule checks that the sensitivity list of a process contains the signals the process needs, and no others.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP8.

A combinational process needs every signal it reads; a missing signal makes simulation differ from the synthesized hardware.
A clocked process needs only its clock and the signals tested before the clock edge, such as an asynchronous reset.
Processes with :code:`process (all)` or a wait statement are not checked.
Names declared outside the file, other than the ports of the entity, cannot be told apart from constants and are not reported missing.

**Violation**

.. code-block:: vhdl

   process (clk, rcv_bit_cnt) is
   begin
     if rst = '0' then
       rcv_state <= waiting;
     elsif falling_edge(clk) then
       rcv_state <= rcv_next_state;
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (clk, rst) is
   begin
     if rst = '0' then
       rcv_state <= waiting;
     elsif falling_edge(clk) then
       rcv_state <= rcv_next_state;
     end if;
   end process;

lint_003
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_unconnected_input_port`

This rule checks that every input port of an instance is connected.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP11.

An input or inout port that is missing from the port map, or mapped to :code:`open`, is left floating or takes its default value.
The ports of the instantiated unit are taken from the file or from the other files of the run.
Instances of units whose ports are not known are not checked.

**Violation**

.. code-block:: vhdl

   u_bad : usable_vhd
     port map (
       in1  => d,
       out1 => q1,
       out2 => q2
     );

**Fix**

.. code-block:: vhdl

   u_bad : usable_vhd
     port map (
       in1  => d,
       in2  => addr,
       out1 => q1,
       out2 => q2
     );

lint_004
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_unconnected_output_port`

This rule checks that every output port of an instance is connected.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP12.

An output, buffer or inout port that is missing from the port map, or mapped to :code:`open`, is not used.
That is sometimes intended, for example for a debug output, and should then be justified.
The ports of the instantiated unit are taken from the file or from the other files of the run.

**Violation**

.. code-block:: vhdl

   u_bad : usable_vhd
     port map (
       in1  => d,
       in2  => addr,
       out1 => open,
       out2 => q
     );

**Fix**

.. code-block:: vhdl

   u_bad : usable_vhd
     port map (
       in1  => d,
       in2  => addr,
       out1 => q1,
       out2 => q
     );

lint_005
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_case_without_others`

This rule checks that every case statement has a :code:`when others` choice.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

Without :code:`when others`, the behaviour for values that are not listed, such as an illegal state after a single event upset, depends on the synthesis tool.
This includes case statements whose choices list every value of an enumerated type.

**Violation**

.. code-block:: vhdl

   case addr is
     when "00" => sel <= '1';
     when "01" => sel <= '0';
   end case;

**Fix**

.. code-block:: vhdl

   case addr is
     when "00" => sel <= '1';
     when "01" => sel <= '0';
     when others => sel <= '0';
   end case;

lint_006
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_duplicate_case_choice`

This rule checks that no choice appears twice in a case statement.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

Choices are compared as written, ignoring case and spaces.
Overlapping ranges are not detected.

**Violation**

.. code-block:: vhdl

   case addr is
     when "000" => clk_div_en <= '1';
     when "001" => clk_div_en <= '1';
     when "000" => clk_div_en <= '0';
     when others => clk_div_en <= '0';
   end case;

**Fix**

.. code-block:: vhdl

   case addr is
     when "000" => clk_div_en <= '1';
     when "001" => clk_div_en <= '1';
     when others => clk_div_en <= '0';
   end case;

lint_007
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_unreachable_case_choice`

This rule checks for case choices that can never be reached in hardware.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

A string or character choice containing a metavalue, such as X, Z, U, W or -, never matches a real signal value.
In a matching case statement, :code:`case?`, the - is a don't care and is allowed.

**Violation**

.. code-block:: vhdl

   case addr is
     when "000" => sel <= '1';
     when "10X" => sel <= '0';
     when others => sel <= '0';
   end case;

**Fix**

.. code-block:: vhdl

   case addr is
     when "000" => sel <= '1';
     when others => sel <= '0';
   end case;

lint_008
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_combinational_feedback`

This rule checks for combinational feedback: a signal that is read and assigned in the same combinational process or concurrent assignment.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS3.

Such a signal forms a loop without a register, whose behaviour is unpredictable.
Assignments to an element or slice, such as :code:`p(i) <= p(i - 1)`, are not checked, since they may read other elements.
Loops through several processes or assignments are not detected.

**Violation**

.. code-block:: vhdl

   fred_s <= gated_in_s or pulse_r;

   process (en_i, fred_s) is
   begin
     gated_in_s <= fred_s and en_i;
     if en_i = '0' then
       gated_in_s <= not gated_in_s;
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (clk) is
   begin
     if rising_edge(clk) then
       gated_in_r <= not gated_in_r;
     end if;
   end process;

lint_009
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_latch_inference`

This rule checks for latches: signals that a combinational process assigns on some paths but not on all of them.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS4.

A signal keeps its value on the paths that do not assign it, so synthesis infers a latch.
Assign a default value at the start of the process, or assign the signal in every branch.
An assignment to part of a signal, such as :code:`out2(3)`, does not count as assigning the whole signal.
An if statement whose condition reads no signal, such as :code:`if IMPLEMENT_WRITE_G then`, is decided at elaboration and is not a latch.

**Violation**

.. code-block:: vhdl

   process (in1, in2, in3, in4) is
   begin
     if in4 = '0' then
       out1 <= in1;
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (in1, in2, in3, in4) is
   begin
     if in4 = '0' then
       out1 <= in1;
     else
       out1 <= in2;
     end if;
   end process;

lint_010
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_multiple_drivers`

This rule checks that a signal is driven by only one process, concurrent assignment or instance in an architecture.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS6.

Several drivers of the same signal conflict in hardware.
Different fixed parts of a signal, such as :code:`a(0)` and :code:`a(1)`, may be driven separately.
Drivers are only compared when they are in the same branches of the same if and case generate statements,
since which generate statements exist depends on generics; design analysis checks the elaborated design.
A part selected by a name, such as :code:`mem(addr)`, is not checked.

**Violation**

.. code-block:: vhdl

   operate_proc : process (a1) is
   begin
     a3 <= a1 and "10101000";
   end process;

   test_proc : process (a2) is
   begin
     a3 <= a2;
   end process;

**Fix**

.. code-block:: vhdl

   operate_proc : process (a1, a2) is
   begin
     a3 <= (a1 and "10101000") or a2;
   end process;

lint_011
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_mixed_reset_usage`

This rule checks that a reset signal is used with one polarity and one style throughout a file.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS13.

The reset of a clocked process is the signal tested before the clock edge (asynchronous), or the signal with a reset name tested first after it (synchronous).
Using the same reset as active high in one place and active low in another, or both asynchronously and synchronously, causes unintended behaviour around reset.

**Violation**

.. code-block:: vhdl

   if rising_edge(clk_master) then
     if rst_master = '1' then
       q <= '0';
     end if;
   end if;

   if rst_master = '0' then
     q2 <= '0';
   elsif falling_edge(clk_n) then
     q2 <= d2;
   end if;

**Fix**

.. code-block:: vhdl

   if rising_edge(clk_master) then
     if rst_master = '1' then
       q <= '0';
     end if;
   end if;

   if falling_edge(clk_n) then
     if rst_master = '1' then
       q2 <= '0';
     else
       q2 <= d2;
     end if;
   end if;

lint_012
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_unresettable_register`

This rule checks that every register has a reset.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS14.

A register is a signal assigned on the clock edge of a clocked process.
It needs an assignment in the reset branch of that process, or the process needs a reset.
Signals written through an index that is a name, such as :code:`mem(addr)`, are memories and are not checked.
Registers without a reset on purpose, such as synchronizer flip-flops, should be justified.

**Violation**

.. code-block:: vhdl

   process (clk, reset) is
   begin
     if reset = '1' then
       out2 <= (others => '0');
     elsif rising_edge(clk) then
       out2 <= in2;
       out3 <= in1;
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (clk, reset) is
   begin
     if reset = '1' then
       out2 <= (others => '0');
       out3 <= '0';
     elsif rising_edge(clk) then
       out2 <= in2;
       out3 <= in1;
     end if;
   end process;

lint_013
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_initial_value`

This rule checks for initial values on signals and output ports.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS16.

Registers should get their value from an explicit reset, not from an initial value, so that uninitialized values show up in simulation.
Initial values of input ports are defaults for unconnected inputs and are not reported; see lint_003.

**Violation**

.. code-block:: vhdl

   signal count : unsigned(3 downto 0) := (others => '0');

**Fix**

.. code-block:: vhdl

   signal count : unsigned(3 downto 0);

lint_014
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_simulation_only_construct`

This rule checks for constructs that only simulation supports, in code meant for synthesis.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

Wait statements, after delays, transport delays, shared variables, files, access types and signals or variables of type
real are ignored or rejected by synthesis, so simulation and hardware can behave differently.
Constants of type real are allowed, since they are evaluated at elaboration.
Run lint mode on synthesizable code only, or disable this rule for testbenches.

**Violation**

.. code-block:: vhdl

   q <= d after 1 ns;

**Fix**

.. code-block:: vhdl

   q <= d;

lint_015
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_hidden_region`

This rule checks for regions of code hidden from synthesis or from coverage by pragmas.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

Code between :code:`-- synthesis translate_off` and :code:`translate_on` is simulated but not synthesized,
and code between :code:`-- coverage off` and :code:`coverage on` is not counted in coverage.
Each such region should be justified, for example with a comment on the same line as the pragma.

**Violation**

.. code-block:: vhdl

   -- synthesis translate_off
   assert width > 0 report "width must be positive";
   -- synthesis translate_on

lint_016
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_integer_without_range`

This rule checks that integer signals and ports have a range.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

An integer, natural or positive signal without a range synthesizes to 32 bits and hides its real width.
Constants, generics and variables are not checked.

**Violation**

.. code-block:: vhdl

   signal count : natural;

**Fix**

.. code-block:: vhdl

   signal count : natural range 0 to 15;

lint_017
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_state_machine_recovery`

This rule checks that a state machine recovers from illegal states.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

A state machine is a case statement on a signal of an enumerated type declared in the file.
Its :code:`when others` choice must assign a state, so an illegal state caused by a single event upset leads back to a defined state.
Synthesis tools remove that recovery logic unless told to keep it, so the :code:`attributes` option can list attributes,
such as :code:`fsm_safe_state`, of which the state signal must have at least one.

**Violation**

.. code-block:: vhdl

   case state is
     when IDLE => state <= START;
     when START => state <= IDLE;
     when others => null;
   end case;

**Fix**

.. code-block:: vhdl

   case state is
     when IDLE => state <= START;
     when START => state <= IDLE;
     when others => state <= IDLE;
   end case;

lint_018
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_requirement_tag`

This rule checks that entities and processes carry a requirement tag, for traceability to the hardware requirements.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

One of the comment lines directly above the entity or process, or the first comment inside it, must match the
:code:`pattern` option, a regular expression. The default accepts tags such as :code:`-- REQ: HWR-123`.
Set the pattern to the tag format of your project.

**Violation**

.. code-block:: vhdl

   -- Output register
   proc_out : process (clk) is

**Fix**

.. code-block:: vhdl

   -- Output register
   -- REQ: HWR-123
   proc_out : process (clk) is

lint_019
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_buffer_or_inout_port`

This rule checks for buffer and inout ports.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

A buffer port can be replaced by an out port and an internal signal, which every tool handles the same way.
An inout port implies a tri-state driver and belongs only on the top level, for device pins.

**Violation**

.. code-block:: vhdl

   port (
     count : buffer unsigned(3 downto 0)
   );

**Fix**

.. code-block:: vhdl

   port (
     count : out unsigned(3 downto 0)
   );

lint_020
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_clock_edge_style`

This rule checks how processes use clock edges.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

A clock edge should be written with :code:`rising_edge` or :code:`falling_edge`, which ignore transitions from metavalues,
rather than with :code:`clk'event`. A process should use one edge of one clock; registers on other clocks or edges belong in a process of their own.

**Violation**

.. code-block:: vhdl

   if clk'event and clk = '1' then

**Fix**

.. code-block:: vhdl

   if rising_edge(clk) then

lint_021
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_one_entity_per_file`

This rule checks that a file holds one entity, named like the file.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

One entity and its architectures per file, in a file named after the entity, makes a design easy to navigate and review.
Files without an entity, such as packages, are not checked.

**Violation**

A file :code:`top.vhd` that declares the entities :code:`fifo` and :code:`ram`.

**Fix**

The entities in files :code:`fifo.vhd` and :code:`ram.vhd`.

lint_022
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_variable_holds_state`

This rule checks for variables in a clocked process that are read before they are written.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

Such a variable keeps its value from the previous clock edge, so synthesis makes it a register.
That register is easy to overlook, because it has no signal.
Write the variable before reading it, or make the register a signal.

**Violation**

.. code-block:: vhdl

   process (clk) is
     variable count : natural range 0 to 15;
   begin
     if rising_edge(clk) then
       count := count + 1;
     end if;
   end process;

**Fix**

.. code-block:: vhdl

   process (clk) is
   begin
     if rising_edge(clk) then
       count_r <= count_r + 1;
     end if;
   end process;

lint_023
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_generic_assertion`

This rule checks that an entity with generics checks their values with an assertion.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

A generic value outside the range a design supports, such as a width of zero, otherwise goes unnoticed until the hardware fails.
The rule accepts any assert statement in the file, in the entity or in an architecture.

**Violation**

.. code-block:: vhdl

   entity fifo is
     generic (
       DEPTH : positive
     );

**Fix**

.. code-block:: vhdl

   assert DEPTH mod 2 = 0
     report "DEPTH must be a power of two"
     severity failure;

lint_024
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_default_assignment`

This rule checks that a combinational process gives every signal it assigns a default value at its start.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

A default assignment before the if and case statements makes sure every path assigns the signal, so no latch can be inferred,
and shows the value of the signal when no branch changes it.

**Violation**

.. code-block:: vhdl

   process (all) is
   begin
     case state is
       when IDLE => state_next <= START;
       when others => state_next <= IDLE;
     end case;
   end process;

**Fix**

.. code-block:: vhdl

   process (all) is
   begin
     state_next <= state;
     case state is
       when IDLE => state_next <= START;
       when others => state_next <= IDLE;
     end case;
   end process;

lint_025
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_process_all`

This rule checks that combinational processes use :code:`process (all)`.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

The VHDL-2008 sensitivity list :code:`all` is always complete, so simulation and synthesis cannot disagree about it.
Code for tools without VHDL-2008 support should disable this rule.

**Violation**

.. code-block:: vhdl

   process (a, b) is

**Fix**

.. code-block:: vhdl

   process (all) is

lint_026
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_direct_entity_instantiation`

This rule checks that entities are instantiated directly, with :code:`entity work.name`, instead of through a component.

.. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

Direct instantiation needs no component declaration, which could differ from the entity.
Components whose entity is not in the file or the run, such as vendor primitives, are not reported.

**Violation**

.. code-block:: vhdl

   u_fifo : fifo
     port map (

**Fix**

.. code-block:: vhdl

   u_fifo : entity work.fifo
     port map (

lint_027
########

|phase_7| |disabled| |error| |unfixable| |lint|

Alias: :code:`lint_enumerated_state_type`

This rule checks that state machines declare their states with an enumerated type.

.. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP5.

A state machine is a case statement on a signal whose name contains the word state, fsm or st.
Single-bit signals, such as a toggle, are not checked.
With an enumerated type, tools show state names and the synthesis tool chooses the encoding, which can then be changed without editing the code.
Projects that require hard-coded encodings should disable this rule.

**Violation**

.. code-block:: vhdl

   signal state : std_logic_vector(1 downto 0);

**Fix**

.. code-block:: vhdl

   type state_t is (IDLE, START, STOP);
   signal state : state_t;
