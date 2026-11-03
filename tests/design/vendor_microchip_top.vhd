library ieee;
use ieee.std_logic_1164.all;

library polarfire;
use polarfire.components.all;

-- Microchip macros declared by the microchip library of mhsg

entity microchip_top is
  port (
    clk_pad : in  std_logic;
    clk_b   : in  std_logic;
    en      : in  std_logic;
    d       : in  std_logic_vector(7 downto 0);
    q       : out std_logic_vector(19 downto 0)
  );
end entity microchip_top;

architecture rtl of microchip_top is

  -- A clock conditioning circuit core, as Libero generates it
  component PF_CCC_C0 is
    port (
      REF_CLK_0     : in  std_logic;
      OUT0_FABCLK_0 : out std_logic;
      PLL_LOCK_0    : out std_logic
    );
  end component;

  signal clk     : std_logic;
  signal clk_g   : std_logic;
  signal clk_pll : std_logic;
  signal lock    : std_logic;
  signal addr_a  : std_logic_vector(3 downto 0);
  signal pll_q   : std_logic;
  signal sle_q   : std_logic;
  signal dout_a  : std_logic_vector(7 downto 0);
  signal dout_b  : std_logic_vector(7 downto 0);

begin

  u_clkint : CLKINT
    port map (
      Y => clk,
      A => clk_pad
    );

  u_gclkint : GCLKINT
    port map (
      Y  => clk_g,
      A  => clk,
      EN => en
    );

  u_ccc : PF_CCC_C0
    port map (
      REF_CLK_0     => clk,
      OUT0_FABCLK_0 => clk_pll,
      PLL_LOCK_0    => lock
    );

  proc_a : process (clk) is
  begin
    if rising_edge(clk) then
      addr_a <= d(3 downto 0);
    end if;
  end process proc_a;

  -- The PLL clock is derived from clk: no crossing
  proc_pll : process (clk_pll) is
  begin
    if rising_edge(clk_pll) then
      pll_q <= addr_a(0);
    end if;
  end process proc_pll;

  -- LAT, the latch mode, is left for the design to declare
  u_sle : SLE
    port map (
      Q   => sle_q,
      D   => d(4),
      CLK => clk_g,
      EN  => '1',
      ALn => '1',
      ADn => '1',
      SLn => '1',
      SD  => '0',
      LAT => '0'
    );

  -- B_ADDR is timed by B_CLK, clk_b, but driven from clk: a crossing
  u_ram : RAM1K20
    port map (
      A_DOUT   => dout_a,
      B_DOUT   => dout_b,
      A_CLK    => clk,
      A_ADDR   => addr_a,
      A_DIN    => d,
      A_WEN    => '0',
      A_ARST_N => '1',
      B_CLK    => clk_b,
      B_ADDR   => addr_a,
      B_DIN    => d,
      B_WEN    => '0',
      B_ARST_N => '1'
    );

  q <= pll_q & sle_q & lock & '0' & dout_a & dout_b;

end architecture rtl;
