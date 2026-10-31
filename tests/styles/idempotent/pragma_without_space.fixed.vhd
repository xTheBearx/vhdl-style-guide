-- Pragmas written without a space after the dashes are detected as pragmas
-- from the start, so the pragma rules apply in the first fix (issue #78).

package body p is

  function is_simulation return boolean is

    variable ret : boolean;

  begin

    ret := false;

    --synthesis translate_off
    if Is_X('X') then
      ret := true;
    end if;
    --synthesis translate_on

    return ret;

  end function is_simulation;

end package body p;

architecture a of e is

begin

  process (clk) is
  begin

    if rising_edge(clk) then

      --synthesis translate_off
      if (rst = '1') then
        regfile <= (others => '0');
      else
      --synthesis translate_on

        if (we = '1') then
          regfile <= din;
        end if;

      --synthesis translate_off
      end if;
      --synthesis translate_on

    end if;

  end process;

end architecture a;
