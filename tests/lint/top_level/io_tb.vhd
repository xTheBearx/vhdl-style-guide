-- A testbench of io_top, which it instantiates as a component

library ieee;
  use ieee.std_logic_1164.all;

entity io_tb is
end entity io_tb;

architecture sim of io_tb is

  component io_top is
    port (
      clk : in    std_logic;
      pad : inout std_logic
    );
  end component io_top;

  signal clk : std_logic;
  signal pad : std_logic;

begin

  u_top : io_top
    port map (
      clk => clk,
      pad => pad
    );

end architecture sim;
