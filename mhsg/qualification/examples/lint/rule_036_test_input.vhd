
package body util_pkg is

  function parity_bad (data : std_logic_vector) return std_logic is
  begin
    if data'length > 0 then
      return xor data;
    end if;
  end function parity_bad;

  function parity_good (data : std_logic_vector) return std_logic is
  begin
    if data'length > 0 then
      return xor data;
    else
      return '0';
    end if;
  end function parity_good;

  procedure pause is
  begin
    wait for 10 ns;
  end procedure pause;

end package body util_pkg;
