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
