
package pkg is

  function my_func is new my_generic_func
    generic map (
      test => 2
    );

  procedure my_proc is new my_generic_proc;

  -- Violations below

  function my_func is new my_generic_func
    generic map (
      test => 2
    );

  constant c_test2 : integer;
  procedure my_proc is new my_generic_proc;

  procedure my_proc2 is new my_generic_proc;

end package pkg;
