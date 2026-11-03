
architecture rtl of fifo is

begin

  process (addr) is
  begin
    case addr is
      when "000" =>
        sel <= '1';
      when "001" | "010" =>
        sel <= '0';
      when "000" =>
        sel <= '1';
      when "10X" =>
        sel <= '0';
    end case;
    case? addr is
      when "1--" =>
        y <= '1';
      when "0-Z" =>
        y <= '0';
      when others =>
        y <= '0';
    end case?;
  end process;

end architecture rtl;
