
library ieee;
  use ieee.std_logic_1164.all;

entity assertion_top is
  port (
    clk : in    std_logic;
    d   : in    std_logic;
    q   : out   std_logic
  );
end entity assertion_top;

architecture rtl of assertion_top is

begin

  -- GHDL holds the condition of each assert in a register, which only feeds the assertion; with a condition that is
  -- always true, as here, the register is constant
  process is
  begin

    wait until rising_edge(clk);
    assert true report "never fails";
    q <= d;

  end process;

end architecture rtl;
