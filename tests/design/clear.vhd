library ieee;
use ieee.std_logic_1164.all;

-- A synchronous clear from logic, listed under clears, is followed like data; a synchronized reset is not

entity clear_top is
  port (
    clk_a : in  std_logic;
    clk_b : in  std_logic;
    in_a  : in  std_logic_vector(2 downto 0);
    hold  : in  std_logic;
    q     : out std_logic_vector(3 downto 0)
  );
end entity clear_top;

architecture rtl of clear_top is

  signal x_a      : std_logic;
  signal y_a      : std_logic;
  signal rst_a    : std_logic;
  signal x_meta   : std_logic;
  signal x_b      : std_logic;
  signal y_meta   : std_logic;
  signal y_b      : std_logic;
  signal rst_meta : std_logic;
  signal rst_b    : std_logic;
  signal clr_b    : std_logic;
  signal r1_b     : std_logic;
  signal r2_b     : std_logic;
  signal r3_b     : std_logic;
  signal r4_b     : std_logic;

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      x_a   <= in_a(0);
      y_a   <= in_a(1);
      rst_a <= in_a(2);
    end if;
  end process proc_a;

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      x_meta   <= x_a;
      x_b      <= x_meta;
      y_meta   <= y_a;
      y_b      <= y_meta;
      rst_meta <= rst_a;
      rst_b    <= rst_meta;
      -- A clear computed from a synchronized signal: x_a and y_a meet in r1_b and r2_b
      clr_b <= x_b and not hold;
      if clr_b = '1' then
        r1_b <= '0';
        r2_b <= '0';
      else
        r1_b <= y_b;
        r2_b <= not y_b;
      end if;
      -- A synchronized reset: not followed
      if rst_b = '1' then
        r3_b <= '0';
        r4_b <= '0';
      else
        r3_b <= y_b;
        r4_b <= not y_b;
      end if;
    end if;
  end process proc_b;

  q <= r1_b & r2_b & r3_b & r4_b;

end architecture rtl;
