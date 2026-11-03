
architecture rtl of top is

begin

  proc_event : process (clk) is
  begin
    if clk'event and clk = '1' then
      a <= b;
    end if;
  end process;

  proc_two : process (clk1, clk2) is
  begin
    if rising_edge(clk1) then
      a <= b;
    end if;
    if rising_edge(clk2) then
      c <= d;
    end if;
  end process;

  proc_good : process (clk) is
  begin
    if rising_edge(clk) then
      e <= f;
    end if;
  end process;

end architecture rtl;
