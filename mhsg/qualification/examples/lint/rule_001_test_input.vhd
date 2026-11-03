
architecture rtl of fifo is

begin

  process (reset, a) is
  begin
    same_signal <= '0';
    if reset = '1' then
      same_signal <= '1';
    end if;
    if reset = '1' then
      beep <= '0';
      beep <= '1';
      vec(0) <= '0';
      vec(1) <= '1';
    end if;
  end process;

end architecture rtl;
