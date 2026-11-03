-- Qualification example of design_007: a register fed by 64 levels of logic, more than the limit of 48

library ieee;
  use ieee.std_logic_1164.all;

entity deep_top is
  port (
    clk : in    std_logic;
    a   : in    std_logic_vector(63 downto 0);
    b   : in    std_logic_vector(63 downto 0);
    q   : out   std_logic
  );
end entity deep_top;

architecture rtl of deep_top is

begin

  -- Each step combines the result of the one before it, so the chain is 64 operators deep
  process (clk) is
    variable chain : std_logic;
  begin
    if rising_edge(clk) then
      chain := '0';
      for i in 0 to 63 loop
        chain := (chain xor a(i)) and b(i);
      end loop;
      q <= chain;
    end if;
  end process;

end architecture rtl;
