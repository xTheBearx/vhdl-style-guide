
architecture rtl of fifo is

begin

  fred_s <= gated_in_s or pulse_r;
  count  <= count + 1;

  process (en_i, fred_s, gated_in_s) is
  begin
    gated_in_s <= fred_s and en_i;
    if en_i = '0' then
      gated_in_s <= not gated_in_s;
    end if;
    other <= en_i;
  end process;

  process (clk) is
  begin
    if rising_edge(clk) then
      cnt <= cnt + 1;
    end if;
  end process;

end architecture rtl;
