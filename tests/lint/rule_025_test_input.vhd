
architecture rtl of top is

begin

  process (a, b) is
  begin
    c <= a and b;
  end process;

  process (all) is
  begin
    d <= a or b;
  end process;

  process (clk) is
  begin
    if rising_edge(clk) then
      e <= a;
    end if;
  end process;

end architecture rtl;
