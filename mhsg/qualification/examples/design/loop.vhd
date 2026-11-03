library ieee;
use ieee.std_logic_1164.all;

entity loop_pass is
  port (
    a : in  std_logic;
    y : out std_logic
  );
end entity loop_pass;

architecture rtl of loop_pass is
begin

  y <= not a;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity loop_top is
  port (
    c : in  std_logic;
    d : in  std_logic;
    q : out std_logic;
    r : out std_logic
  );
end entity loop_top;

architecture rtl of loop_top is

  signal a : std_logic;
  signal b : std_logic;
  signal e : std_logic;
  signal f : std_logic;

begin

  -- A loop through two concurrent assignments
  a <= b and c;
  b <= a or d;
  q <= b;

  -- A loop through an instance of another entity
  e <= f xor c;

  u_pass : entity work.loop_pass
    port map (
      a => e,
      y => f
    );

  r <= f;

end architecture rtl;
