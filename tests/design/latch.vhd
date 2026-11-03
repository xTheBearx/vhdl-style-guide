library ieee;
use ieee.std_logic_1164.all;

entity latch_top is
  port (
    a, en : in  std_logic;
    q, r  : out std_logic
  );
end entity latch_top;

architecture rtl of latch_top is
begin

  proc_latch : process (all) is
  begin
    if en = '1' then
      q <= a;
    end if;
  end process proc_latch;

  r <= not a;

end architecture rtl;
