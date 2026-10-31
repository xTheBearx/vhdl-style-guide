
architecture arch of minimal is

  function calc_out_function return integer is

    function nested_function_function return integer is
    begin
      return 5;
    end function;

  begin
    return 2 * nested_function_function;
  end function;

begin

end architecture arch;
