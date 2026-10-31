
package pkg is

  constant c_test1 : integer;

  function my_func is new my_generic_func
    generic map (
      test => 2
    );

  -- Comment
  procedure my_proc is new my_generic_proc;

  -- Violations below

  constant c_test2 : integer;

  function my_func is new my_generic_func
    generic map (
      test => 2
    );

  procedure my_proc is new my_generic_proc;

end package pkg;

package body pkg is

  function f return integer is
  begin
    return 1;
  end function f;

end package body pkg;
