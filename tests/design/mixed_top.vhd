-- A VHDL top level using a Verilog module, see mixed_sync.v

library ieee;
  use ieee.std_logic_1164.all;

entity mixed_top is
  port (
    clk_a  : in    std_logic;
    clk_b  : in    std_logic;
    in_a   : in    std_logic;
    sync_b : out   std_logic;
    raw_b  : out   std_logic
  );
end entity mixed_top;

architecture rtl of mixed_top is

  component mixed_sync is
    port (
      clk : in    std_logic;
      d   : in    std_logic;
      q   : out   std_logic
    );
  end component mixed_sync;

  signal flag_a : std_logic;
  signal raw    : std_logic;

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      flag_a <= in_a;
    end if;
  end process proc_a;

  u_sync : component mixed_sync
    port map (
      clk => clk_b,
      d   => flag_a,
      q   => sync_b
    );

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      raw   <= flag_a;
      raw_b <= raw and flag_a;
    end if;
  end process proc_b;

end architecture rtl;
