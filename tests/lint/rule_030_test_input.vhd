
architecture rtl of e is
begin

  process (all) is
  begin
    if a = '1' then
      if b = '1' then
        case c is
          when "00" =>
            if d = '1' then
              for i in 0 to 3 loop
                y(i) <= e(i);
              end loop;
            end if;
          when others =>
            null;
        end case;
      end if;
    end if;
  end process;

end architecture rtl;
