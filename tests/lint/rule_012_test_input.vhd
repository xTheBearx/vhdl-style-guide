
architecture rtl of top is

begin

  process (clk, reset) is
  begin
    if reset = '1' then
      out2 <= (others => '0');
    elsif rising_edge(clk) then
      out2 <= in2;
      out3 <= in1;
      mem(addr) <= in1;
    end if;
  end process;

  process (clk) is
  begin
    if rising_edge(clk) then
      sync1 <= async_in;
    end if;
  end process;

  process (clk) is
  begin
    if rising_edge(clk) then
      if rst = '1' then
        count <= (others => '0');
      else
        count <= count + 1;
        flag  <= '1';
      end if;
    end if;
  end process;

end architecture rtl;
