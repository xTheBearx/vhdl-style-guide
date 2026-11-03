
architecture rtl of e is
  constant c_last : natural := 99;
  signal count : natural range 0 to 99;
begin

  process (clk) is
  begin
    if rising_edge(clk) then
      if count = 99 then
        count <= 0;
      elsif count = c_last then
        count <= count + 1;
      end if;
      data <= bus_in(7 downto 4);
    end if;
  end process;

  y <= x after 10 ns;

end architecture rtl;
