-- Qualification example of case_022: the first case statement has no label, the second has one

architecture rtl of decoder is
begin

  process (all) is
  begin
    case address is
      when "00" =>
        sel <= "0001";
      when others =>
        sel <= "0000";
    end case;
    address_decode : case address is
      when "00" =>
        sel2 <= "0001";
      when others =>
        sel2 <= "0000";
    end case address_decode;
  end process;

end architecture rtl;
