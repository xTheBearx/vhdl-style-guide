library ieee;
use ieee.std_logic_1164.all;

-- Clocks, latches and pins in test mode: scan_mode selects test mode and scan_en the shift of the scan chains. Each
-- case comes controlled in test mode and not
entity starc_dft_top is
  port (
    clk       : in    std_logic;
    clk2      : in    std_logic;
    scan_mode : in    std_logic;
    scan_en   : in    std_logic;
    d         : in    std_logic;
    q         : out   std_logic_vector(10 downto 0);
    pin       : inout std_logic;
    pin2      : inout std_logic
  );
end entity starc_dft_top;

architecture rtl of starc_dft_top is

  signal div_q   : std_logic := '0';
  signal div2_q  : std_logic := '0';
  signal div_clk : std_logic;
  signal en_r    : std_logic;
  signal sel_r   : std_logic;
  signal oe_r    : std_logic;
  signal g_r     : std_logic;
  signal gclk    : std_logic;
  signal gclk2   : std_logic;
  signal mclk    : std_logic;
  signal r       : std_logic_vector(5 downto 0);
  signal lt      : std_logic;
  signal li      : std_logic;
  signal lb      : std_logic;

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      div_q  <= not div_q;
      div2_q <= not div2_q;
      en_r   <= d;
      sel_r  <= not d;
      oe_r   <= d xor div_q;
      g_r    <= d and div_q;
    end if;
  end process;

  -- Divided clocks: one selected away in test mode, one not
  div_clk <= clk when scan_mode = '1' else div_q;

  process (div_clk) is
  begin
    if rising_edge(div_clk) then
      r(0) <= d;
    end if;
  end process;

  process (div2_q) is
  begin
    if rising_edge(div2_q) then
      r(1) <= d;
    end if;
  end process;

  -- Gated clocks: one forced on in test mode, one not
  gclk  <= clk and (en_r or scan_mode);
  gclk2 <= clk and en_r;

  process (gclk) is
  begin
    if rising_edge(gclk) then
      r(2) <= d;
    end if;
  end process;

  process (gclk2) is
  begin
    if rising_edge(gclk2) then
      r(3) <= d;
    end if;
  end process;

  -- A clock multiplexer whose select is a register
  mclk <= clk when sel_r = '1' else clk2;

  process (mclk) is
  begin
    if rising_edge(mclk) then
      r(4) <= d;
    end if;
  end process;

  -- The other edge of clk
  process (clk) is
  begin
    if falling_edge(clk) then
      r(5) <= d;
    end if;
  end process;

  -- Latches: transparent in test mode, on the inverted clock, and on a register
  process (g_r, scan_mode, d) is
  begin
    if (g_r or scan_mode) = '1' then
      lt <= d;
    end if;
  end process;

  process (clk, d) is
  begin
    if clk = '0' then
      li <= d;
    end if;
  end process;

  process (g_r, d) is
  begin
    if g_r = '1' then
      lb <= d;
    end if;
  end process;

  -- Pins: one released during scan shift, one not
  pin  <= d when (oe_r and not scan_en) = '1' else 'Z';
  pin2 <= d when oe_r = '1' else 'Z';

  q <= pin2 & pin & lb & li & lt & r;

end architecture rtl;
