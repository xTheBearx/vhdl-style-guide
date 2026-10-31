
package pkg is

  type state_t is (idle, run);
  type mode is (a, b);

end package pkg;

package body pkg is

  type local is (x, y);

  function f return integer is
    type tmp is (p, q);
  begin
    return 1;
  end function f;

end package body pkg;

architecture rtl of e is

  type arch is (m, n);

begin
end architecture rtl;
