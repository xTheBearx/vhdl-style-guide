library ieee;
use ieee.std_logic_1164.all;

-- A block whose ID, AB, extends the ID of the top, A; its output is computed by logic from its register
entity AB_regs is
  port (
    clk     : in    std_logic;
    d       : in    std_logic;
    en      : in    std_logic;
    AB_data : out   std_logic
  );
end entity AB_regs;

architecture rtl of AB_regs is

  signal r : std_logic;

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      r <= d;
    end if;
  end process;

  AB_data <= r and en;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

-- A block whose ID, C, does not extend A; it registers logic of its input
entity C_logic is
  port (
    clk    : in    std_logic;
    a      : in    std_logic;
    b      : in    std_logic;
    C_data : out   std_logic
  );
end entity C_logic;

architecture rtl of C_logic is

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      C_data <= a xor b;
    end if;
  end process;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity A_top is
  port (
    clk    : in    std_logic;
    d      : in    std_logic;
    en     : in    std_logic;
    b      : in    std_logic;
    A_q    : out   std_logic;
    badout : out   std_logic
  );
end entity A_top;

architecture rtl of A_top is

  signal ab_out : std_logic;
  signal glue   : std_logic;
  signal C_data : std_logic;

begin

  -- AB_data drives a net of another name
  u_ab : entity work.AB_regs
    port map (
      clk     => clk,
      d       => d,
      en      => en,
      AB_data => ab_out
    );

  -- Logic in the top between the instances: the path from the register of u_ab to the register of u_c spans three
  -- blocks
  glue <= ab_out or d;

  u_c : entity work.C_logic
    port map (
      clk    => clk,
      a      => glue,
      b      => b,
      C_data => C_data
    );

  A_q    <= C_data;
  badout <= ab_out;

end architecture rtl;
