library ieee;
use ieee.std_logic_1164.all;

-- A register feeds a black box whose output nothing reads: the register is not used. Another feeds a black box with no
-- output, such as a debug core: it is used
entity box_unused_top is
  port (
    clk : in    std_logic;
    a   : in    std_logic;
    b   : in    std_logic;
    q   : out   std_logic
  );
end entity box_unused_top;

architecture rtl of box_unused_top is

  component BOX_FILTER is
    port (
      CLK : in    std_logic;
      D   : in    std_logic;
      Q   : out   std_logic
    );
  end component;

  component BOX_PROBE is
    port (
      CLK   : in    std_logic;
      PROBE : in    std_logic
    );
  end component;

  signal a_r      : std_logic;
  signal b_r      : std_logic;
  signal filtered : std_logic;

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      a_r <= a;
      b_r <= b;
    end if;
  end process;

  u_filter : component BOX_FILTER
    port map (
      CLK => clk,
      D   => a_r,
      Q   => filtered
    );

  u_probe : component BOX_PROBE
    port map (
      CLK   => clk,
      PROBE => b_r
    );

  q <= b;

end architecture rtl;
