library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity cdc_top is
  port (
    clk_a   : in  std_logic;
    clk_b   : in  std_logic;
    clk_c   : in  std_logic;
    rst_a   : in  std_logic;
    rst_c   : in  std_logic;
    in_a    : in  std_logic_vector(7 downto 0);
    start_a : in  std_logic;
    en_a    : in  std_logic;
    result  : out std_logic_vector(31 downto 0)
  );
end entity cdc_top;

architecture rtl of cdc_top is

  -- Clock domain a
  signal flag_a    : std_logic;
  signal x_a       : std_logic;
  signal y_a       : std_logic;
  signal bus_a     : std_logic_vector(3 downto 0);
  signal bin_a     : unsigned(3 downto 0);
  signal gray_a    : std_logic_vector(3 downto 0);
  signal data_a    : std_logic_vector(7 downto 0);
  signal req_a     : std_logic;
  signal gate_en_a : std_logic;
  signal div_a     : std_logic;
  signal sample_a  : std_logic;
  signal raw_a     : std_logic;
  signal soft_a    : std_logic;
  signal gen_a     : std_logic;

  -- Clock domain b
  signal unsync_b  : std_logic;
  signal sync1_b   : std_logic;
  signal sync2_b   : std_logic;
  signal logic1_b  : std_logic;
  signal logic2_b  : std_logic;
  signal bus1_b    : std_logic_vector(3 downto 0);
  signal bus2_b    : std_logic_vector(3 downto 0);
  signal gray1_b   : std_logic_vector(3 downto 0);
  signal gray2_b   : std_logic_vector(3 downto 0);
  signal req1_b    : std_logic;
  signal req2_b    : std_logic;
  signal req3_b    : std_logic;
  signal data_b    : std_logic_vector(7 downto 0);
  signal rsync1_b  : std_logic;
  signal rsync2_b  : std_logic;
  signal rst_b     : std_logic;
  signal clean_b   : std_logic;
  signal cross_a   : std_logic;

  -- Derived clocks
  signal clk_gated : std_logic;
  signal gated_q   : std_logic;
  signal div_q     : std_logic;
  signal shared_q  : std_logic;
  signal shared_r  : std_logic;

begin

  -- Domain a, with a synchronous reset
  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      flag_a    <= in_a(0);
      x_a       <= in_a(1);
      y_a       <= in_a(2);
      bus_a     <= in_a(7 downto 4);
      bin_a     <= bin_a + 1;
      gray_a    <= std_logic_vector(bin_a xor ('0' & bin_a(3 downto 1)));
      if start_a = '1' then
        data_a <= in_a;
        req_a  <= not req_a;
      end if;
      gate_en_a <= en_a;
      div_a     <= not div_a;
      sample_a  <= clk_b;
    end if;
  end process proc_a;

  -- Domain b
  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      unsync_b <= flag_a;
      sync1_b  <= flag_a;
      sync2_b  <= sync1_b;
      logic1_b <= x_a and y_a;
      logic2_b <= logic1_b;
      bus1_b   <= bus_a;
      bus2_b   <= bus1_b;
      gray1_b  <= gray_a;
      gray2_b  <= gray1_b;
      req1_b   <= req_a;
      req2_b   <= req1_b;
      req3_b   <= req2_b;
      if (req2_b xor req3_b) = '1' then
        data_b <= data_a;
      end if;
    end if;
  end process proc_b;

  -- A reset synchronizer for domain b: asserted by rst_a, released on clk_b
  proc_reset_b : process (clk_b, rst_a) is
  begin
    if rst_a = '1' then
      rsync1_b <= '1';
      rsync2_b <= '1';
    elsif rising_edge(clk_b) then
      rsync1_b <= '0';
      rsync2_b <= rsync1_b;
    end if;
  end process proc_reset_b;

  rst_b <= rsync2_b;

  -- Reset by the synchronized reset of its own domain: no finding
  proc_clean_b : process (clk_b, rst_b) is
  begin
    if rst_b = '1' then
      clean_b <= '0';
    elsif rising_edge(clk_b) then
      clean_b <= unsync_b;
    end if;
  end process proc_clean_b;

  -- Reset by the raw reset input: released asynchronously
  proc_raw_a : process (clk_a, rst_a) is
  begin
    if rst_a = '1' then
      raw_a <= '0';
    elsif rising_edge(clk_a) then
      raw_a <= in_a(3);
    end if;
  end process proc_raw_a;

  -- Reset by the reset synchronized to the other domain
  proc_cross_a : process (clk_a, rst_b) is
  begin
    if rst_b = '1' then
      cross_a <= '0';
    elsif rising_edge(clk_a) then
      cross_a <= in_a(5);
    end if;
  end process proc_cross_a;

  -- Reset made by logic
  proc_soft_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      soft_a <= in_a(6);
    end if;
  end process proc_soft_a;

  proc_gen_a : process (clk_a, soft_a, rsync2_b) is
  begin
    if (soft_a or rsync2_b) = '1' then
      gen_a <= '0';
    elsif rising_edge(clk_a) then
      gen_a <= in_a(7);
    end if;
  end process proc_gen_a;

  -- A gated clock
  clk_gated <= clk_a and gate_en_a;

  proc_gated : process (clk_gated) is
  begin
    if rising_edge(clk_gated) then
      gated_q <= in_a(0);
    end if;
  end process proc_gated;

  -- A clock divided by a register
  proc_div : process (div_a) is
  begin
    if rising_edge(div_a) then
      div_q <= flag_a;
    end if;
  end process proc_div;

  -- clk_c is a clock and a reset
  proc_shared_q : process (clk_c) is
  begin
    if rising_edge(clk_c) then
      shared_q <= in_a(1);
    end if;
  end process proc_shared_q;

  proc_shared_r : process (clk_a, clk_c) is
  begin
    if clk_c = '1' then
      shared_r <= '0';
    elsif rising_edge(clk_a) then
      shared_r <= in_a(2);
    end if;
  end process proc_shared_r;

  result <= unsync_b & sync2_b & logic2_b & bus2_b & gray2_b & data_b & clean_b & raw_a & cross_a & gen_a &
            gated_q & div_q & sample_a & shared_q & shared_r & rst_c & "000";

end architecture rtl;
