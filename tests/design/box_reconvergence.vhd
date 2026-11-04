library ieee;
use ieee.std_logic_1164.all;

-- Two signals synchronized separately into clk_b meet inside a black box that samples both on one clock pin, and
-- not in a box that samples them on different pins

entity box_reconvergence_top is
  port (
    clk_a : in  std_logic;
    clk_b : in  std_logic;
    in_a  : in  std_logic_vector(1 downto 0);
    y     : out std_logic_vector(1 downto 0)
  );
end entity box_reconvergence_top;

architecture rtl of box_reconvergence_top is

  component SAMPLER is
    port (
      CLK  : in  std_logic;
      CLK2 : in  std_logic;
      A    : in  std_logic;
      B    : in  std_logic;
      Y    : out std_logic
    );
  end component;

  signal start_a    : std_logic;
  signal mode_a     : std_logic;
  signal start_meta : std_logic;
  signal start_b    : std_logic;
  signal mode_meta  : std_logic;
  signal mode_b     : std_logic;

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      start_a <= in_a(0);
      mode_a  <= in_a(1);
    end if;
  end process proc_a;

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      start_meta <= start_a;
      start_b    <= start_meta;
      mode_meta  <= mode_a;
      mode_b     <= mode_meta;
    end if;
  end process proc_b;

  u_same : SAMPLER
    port map (
      CLK  => clk_b,
      CLK2 => clk_b,
      A    => start_b,
      B    => mode_b,
      Y    => y(0)
    );

  u_apart : component SAMPLER
    port map (
      CLK  => clk_b,
      CLK2 => clk_b,
      A    => start_b,
      B    => mode_b,
      Y    => y(1)
    );

end architecture rtl;
