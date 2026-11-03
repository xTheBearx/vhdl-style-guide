library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity depth_adder is
  port (
    a : in  unsigned(7 downto 0);
    b : in  unsigned(7 downto 0);
    y : out unsigned(7 downto 0)
  );
end entity depth_adder;

architecture rtl of depth_adder is
begin

  y <= (a + b) + (a - b);

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity depth_top is
  port (
    clk : in  std_logic;
    a   : in  unsigned(7 downto 0);
    b   : in  unsigned(7 downto 0);
    q   : out unsigned(7 downto 0)
  );
end entity depth_top;

architecture rtl of depth_top is

  signal a_r : unsigned(7 downto 0);
  signal b_r : unsigned(7 downto 0);
  signal sum : unsigned(7 downto 0);

begin

  u_adder : entity work.depth_adder
    port map (
      a => a_r,
      b => b_r,
      y => sum
    );

  proc_regs : process (clk) is
  begin
    if rising_edge(clk) then
      a_r <= a;
      b_r <= b;
      q   <= sum + a_r;
    end if;
  end process proc_regs;

end architecture rtl;
