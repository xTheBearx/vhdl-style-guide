
architecture rtl of top is

begin

  proc1 : process (clk_master) is
  begin
    if rising_edge(clk_master) then
      if rst_master = '1' then
        q <= '0';
      else
        q <= d1;
      end if;
    end if;
  end process;

  proc2 : process (clk_n, rst_master) is
  begin
    if rst_master = '0' then
      q2 <= '0';
    elsif falling_edge(clk_n) then
      q2 <= d2;
    end if;
  end process;

  proc3 : process (clk_master, rst_master) is
  begin
    if rst_master = '1' then
      q3 <= '0';
    elsif rising_edge(clk_master) then
      q3 <= d3;
    end if;
  end process;

end architecture rtl;
