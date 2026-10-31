
package pkg is

  type t_state is (idle, run);

  signal s_state : t_state;
  signal s_data  : STD_LOGIC_VECTOR(7 downto 0);

  function f (a : INTEGER) return t_state;

end package pkg;

package body pkg is

  function f (a : integer) return t_state is
    variable v : NATURAL;
  begin
    return idle;
  end function f;

end package body pkg;
