-- Qualification example of case_023: the first labelled case statement does not repeat its label at its end, the second does

architecture rtl of decoder is
begin

  process (all) is
  begin
    first_decode : case address is
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
