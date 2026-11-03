library util;
use util.order_pkg.all;

entity order_top is
  port (
    clk : in  bit;
    d   : in  bit_vector(WIDTH - 1 downto 0);
    q   : out bit_vector(WIDTH - 1 downto 0)
  );
end entity order_top;

architecture rtl of order_top is
begin

  u_leaf : entity work.order_leaf
    port map (
      clk => clk,
      d   => d,
      q   => q
    );

end architecture rtl;
