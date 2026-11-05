library ieee;
use ieee.std_logic_1164.all;

-- A RAM in a submodule
entity starc2_ram is
  port (
    clk  : in    std_logic;
    we   : in    std_logic;
    addr : in    integer range 0 to 15;
    din  : in    std_logic;
    dout : out   std_logic
  );
end entity starc2_ram;

architecture rtl of starc2_ram is

  type ram_t is array (0 to 15) of std_logic;

  signal ram : ram_t;

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      if we = '1' then
        ram(addr) <= din;
      end if;
      dout <= ram(addr);
    end if;
  end process;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity starc2_top is
  port (
    clk_a : in    std_logic;
    clk_b : in    std_logic;
    g     : in    std_logic;
    d     : in    std_logic;
    oe    : in    std_logic;
    we    : in    std_logic;
    addr  : in    integer range 0 to 15;
    pin   : inout std_logic;
    pin_r : inout std_logic;
    q     : out   std_logic_vector(5 downto 0)
  );
end entity starc2_top;

architecture rtl of starc2_top is

  signal l1   : std_logic;
  signal l2   : std_logic;
  signal l3   : std_logic;
  signal la   : std_logic;
  signal lb   : std_logic;
  signal oe_r : std_logic;
  signal b_r  : std_logic;

begin

  -- Three latches on the same phase: one more than allowed
  process (g, d) is
  begin
    if g = '1' then
      l1 <= d;
    end if;
  end process;

  process (g, l1) is
  begin
    if g = '1' then
      l2 <= not l1;
    end if;
  end process;

  process (g, l2) is
  begin
    if g = '1' then
      l3 <= l2;
    end if;
  end process;

  -- A loop through a latch
  process (g, lb) is
  begin
    if g = '1' then
      la <= not lb;
    end if;
  end process;

  lb <= la and d;

  -- A tri-state enable from a register; the bidirectional net is read in the same module
  process (clk_a) is
  begin
    if rising_edge(clk_a) then
      oe_r <= oe;
    end if;
  end process;

  pin_r <= d when oe_r = '1' else 'Z';
  pin   <= d when oe = '1' else 'Z';

  -- Registers of a second clock domain in the top-level module
  process (clk_b) is
  begin
    if rising_edge(clk_b) then
      b_r <= pin and d;
    end if;
  end process;

  u_ram : entity work.starc2_ram
    port map (
      clk  => clk_a,
      we   => we,
      addr => addr,
      din  => d,
      dout => q(5)
    );

  q(0) <= l3;
  q(1) <= la;
  q(2) <= b_r;
  q(3) <= oe_r;
  q(4) <= pin_r;

end architecture rtl;
