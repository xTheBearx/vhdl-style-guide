library ieee;
use ieee.std_logic_1164.all;

entity undeclared_top is
  port (
    a : in  std_logic;
    q : out std_logic
  );
end entity undeclared_top;

architecture rtl of undeclared_top is
begin

  q <= a and missing_signal;

end architecture rtl;
