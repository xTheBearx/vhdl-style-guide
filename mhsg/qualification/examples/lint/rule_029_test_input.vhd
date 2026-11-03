
architecture rtl of e is
begin

  pulse <= '1', '0' after 10 ns;
  level <= '1';

  process (all) is
  begin
    strobe <= '0', '1' after 5 ns, '0' after 10 ns;
  end process;

end architecture rtl;
