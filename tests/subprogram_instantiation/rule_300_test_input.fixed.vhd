
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

  procedure my_proc is new my_generic_proc;

end package pkg;

architecture rtl of ent is

  function my_func is new my_generic_func;

begin

  process is

    procedure my_proc is new my_generic_proc;

  begin
  end process;

end architecture rtl;
