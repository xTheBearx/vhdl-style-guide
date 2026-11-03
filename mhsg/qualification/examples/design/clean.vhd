library ieee;
use ieee.std_logic_1164.all;

entity clean_top is
  port (
    clk : in  std_logic;
    d   : in  std_logic;
    q   : out std_logic
  );
end entity clean_top;

architecture rtl of clean_top is
begin

  proc_reg : process (clk) is
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process proc_reg;

end architecture rtl;
