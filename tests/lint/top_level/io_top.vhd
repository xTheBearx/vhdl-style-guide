-- The top level of a design: pad is a pin of the device

library ieee;
  use ieee.std_logic_1164.all;

entity io_top is
  port (
    clk : in    std_logic;
    pad : inout std_logic
  );
end entity io_top;

architecture rtl of io_top is

begin

  u_sub : entity work.io_sub
    port map (
      clk  => clk,
      line => pad
    );

end architecture rtl;
