library util;
use util.order_pkg.all;

entity order_leaf is
  port (
    clk : in  bit;
    d   : in  bit_vector(WIDTH - 1 downto 0);
    q   : out bit_vector(WIDTH - 1 downto 0)
  );
end entity order_leaf;

architecture rtl of order_leaf is
begin

  process (clk) is
  begin
    if clk'event and clk = '1' then
      q <= d;
    end if;
  end process;

end architecture rtl;
