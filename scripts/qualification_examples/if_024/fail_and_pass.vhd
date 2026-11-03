-- Qualification example of if_024: code after then on the same line, then the same statement written well

architecture rtl of mux is
begin

  process (all) is
  begin
    if (a = '1') then c <= '1'; else c <= '0'; end if;
    if (a = '1') then
      d <= '1';
    else
      d <= '0';
    end if;
  end process;

end architecture rtl;
