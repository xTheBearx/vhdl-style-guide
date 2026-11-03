library ieee;
use ieee.std_logic_1164.all;

entity real_top is
  generic (
    FREQ_HZ : real;
    RATE_HZ : real    := 1.0e3;
    WIDTH   : positive
  );
  port (
    clk : in  std_logic;
    q   : out std_logic_vector(WIDTH - 1 downto 0)
  );
end entity real_top;

architecture rtl of real_top is

  constant DIVIDE : positive := integer(FREQ_HZ / RATE_HZ);

begin

  proc_count : process (clk) is
    variable count : natural range 0 to DIVIDE - 1 := 0;
  begin
    if rising_edge(clk) then
      if count = DIVIDE - 1 then
        count := 0;
        q     <= (others => '1');
      else
        count := count + 1;
        q     <= (others => '0');
      end if;
    end if;
  end process proc_count;

end architecture rtl;
