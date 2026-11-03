library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity reconvergence_top is
  port (
    clk_a  : in  std_logic;
    clk_b  : in  std_logic;
    in_a   : in  std_logic_vector(3 downto 0);
    result : out std_logic_vector(11 downto 0)
  );
end entity reconvergence_top;

architecture rtl of reconvergence_top is

  signal start_a    : std_logic;
  signal mode_a     : std_logic;
  signal bin_a      : unsigned(3 downto 0);
  signal gray_a     : std_logic_vector(3 downto 0);
  signal start_meta : std_logic;
  signal start_b    : std_logic;
  signal mode_meta  : std_logic;
  signal mode_b     : std_logic;
  signal gray_meta  : std_logic_vector(3 downto 0);
  signal gray_b     : std_logic_vector(3 downto 0);
  signal go_b       : std_logic;
  signal parity_b   : std_logic;
  signal start_d_b  : std_logic;
  signal edge_b     : std_logic;
  signal flag_a     : std_logic;
  signal first1_b   : std_logic;
  signal first2_b   : std_logic;
  signal second1_b  : std_logic;
  signal second2_b  : std_logic;
  signal differ_b   : std_logic;
  signal state_b    : std_logic;
  signal hold_b     : std_logic;
  signal late_b     : std_logic;
  signal later_b    : std_logic;
  signal busy_b     : std_logic;
  signal rst_a      : std_logic;
  signal rst_meta   : std_logic;
  signal rst_b      : std_logic;
  signal count1_b   : std_logic;
  signal count2_b   : std_logic;

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      start_a <= in_a(0);
      mode_a  <= in_a(1);
      bin_a   <= bin_a + 1;
      gray_a  <= std_logic_vector(bin_a xor ('0' & bin_a(3 downto 1)));
      flag_a  <= in_a(2);
      rst_a   <= in_a(3);
    end if;
  end process proc_a;

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      start_meta <= start_a;
      start_b    <= start_meta;
      mode_meta  <= mode_a;
      mode_b     <= mode_meta;
      gray_meta  <= gray_a;
      gray_b     <= gray_meta;
      -- Two signals synchronized separately meet again
      go_b <= start_b and mode_b;
      -- The bits of a gray-coded bus are meant to be combined
      parity_b <= gray_b(0) xor gray_b(1) xor gray_b(2) xor gray_b(3);
      -- One synchronized signal combined with a delayed copy of itself
      start_d_b <= start_b;
      edge_b    <= start_b and not start_d_b;
      -- One signal through two synchronizers: they can disagree for a cycle
      first1_b  <= flag_a;
      first2_b  <= first1_b;
      second1_b <= flag_a;
      second2_b <= second1_b;
      differ_b  <= first2_b xor second2_b;
      -- Two synchronized signals that meet after more registers
      if start_b = '1' then
        state_b <= not state_b;
      end if;
      hold_b <= mode_b;
      late_b <= state_b and hold_b;
      -- Downstream of a meeting: not reported again
      later_b <= late_b;
      -- A flag set by one synchronized signal and cleared by another
      if start_b = '1' then
        busy_b <= '1';
      elsif mode_b = '1' then
        busy_b <= '0';
      end if;
      -- A synchronized synchronous reset of several registers: a reset path, followed only with follow_resets
      rst_meta <= rst_a;
      rst_b    <= rst_meta;
      if rst_b = '1' then
        count1_b <= '0';
        count2_b <= '0';
      else
        count1_b <= start_b;
        count2_b <= not start_b;
      end if;
    end if;
  end process proc_b;

  result <= go_b & parity_b & edge_b & gray_b(0) & start_b & mode_b & differ_b & later_b & late_b & busy_b & count1_b & count2_b;

end architecture rtl;
