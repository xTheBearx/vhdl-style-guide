
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

  procedure my_proc is new my_generic_proc
    generic map (
      test => 2
    );

end package pkg;
