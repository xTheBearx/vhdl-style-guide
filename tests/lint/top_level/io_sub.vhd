-- An entity io_top instantiates: its inout port is inside the design

library ieee;
  use ieee.std_logic_1164.all;

entity io_sub is
  port (
    clk  : in    std_logic;
    line : inout std_logic
  );
end entity io_sub;

architecture rtl of io_sub is

begin

end architecture rtl;
