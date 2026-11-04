library ieee;
use ieee.std_logic_1164.all;

-- A VHDL register with a width generic, through an inner entity, for the Verilog top of vtop_generics.v

entity vtop_leaf is
  generic (
    WIDTH : integer := 4
  );
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(WIDTH - 1 downto 0);
    q   : out std_logic_vector(WIDTH - 1 downto 0)
  );
end entity vtop_leaf;

architecture rtl of vtop_leaf is
begin

  proc_q : process (clk) is
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process proc_q;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity vtop_reg is
  generic (
    WIDTH  : integer := 4;
    INVERT : boolean := false
  );
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(WIDTH - 1 downto 0);
    q   : out std_logic_vector(WIDTH - 1 downto 0)
  );
end entity vtop_reg;

architecture rtl of vtop_reg is

  signal d_in : std_logic_vector(WIDTH - 1 downto 0);

begin

  d_in <= not d when INVERT else d;

  u_leaf : entity work.vtop_leaf
    generic map (
      WIDTH => WIDTH
    )
    port map (
      clk => clk,
      d   => d_in,
      q   => q
    );

end architecture rtl;
