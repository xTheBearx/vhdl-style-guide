library ieee;
use ieee.std_logic_1164.all;

-- An entity with a loop through a black box, instantiated twice: a declaration of one instance of the black box,
-- u_a.u_loop, gives its output a path from its input, so the loop is found through that instance only

entity box_instances_cell is
  port (
    c : in  std_logic;
    q : out std_logic
  );
end entity box_instances_cell;

architecture rtl of box_instances_cell is

  component LUT_BUF is
    port (
      O : out std_logic;
      I : in  std_logic
    );
  end component;

  signal e : std_logic;
  signal f : std_logic;

begin

  e <= f xor c;

  u_loop : LUT_BUF
    port map (
      O => f,
      I => e
    );

  q <= f;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity box_instances_top is
  port (
    c : in  std_logic;
    a : out std_logic;
    b : out std_logic
  );
end entity box_instances_top;

architecture rtl of box_instances_top is
begin

  u_a : entity work.box_instances_cell
    port map (
      c => c,
      q => a
    );

  u_b : entity work.box_instances_cell
    port map (
      c => c,
      q => b
    );

end architecture rtl;
