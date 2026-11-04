library ieee;
use ieee.std_logic_1164.all;

-- A black box declared with a path from its input to its output, such as a buffer: a loop through it, and a path
-- through it to a register, are found only with the declaration

entity box_path_top is
  port (
    clk : in  std_logic;
    c   : in  std_logic;
    d   : in  std_logic;
    q   : out std_logic;
    r   : out std_logic
  );
end entity box_path_top;

architecture rtl of box_path_top is

  component LUT_BUF is
    port (
      O : out std_logic;
      I : in  std_logic
    );
  end component;

  signal e : std_logic;
  signal f : std_logic;
  signal g : std_logic;
  signal h : std_logic;

begin

  -- A loop through the black box
  e <= f xor c;

  u_loop : LUT_BUF
    port map (
      O => f,
      I => e
    );

  q <= f;

  -- Two levels of logic before the black box and one after it
  g <= (c and d) xor d;

  u_path : LUT_BUF
    port map (
      O => h,
      I => g
    );

  proc_r : process (clk) is
  begin
    if rising_edge(clk) then
      r <= h or c;
    end if;
  end process proc_r;

end architecture rtl;
