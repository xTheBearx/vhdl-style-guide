
package pkg is

  constant width_c : integer := 8;
  constant depth : integer := 4;

end package pkg;

package body pkg is

  constant local : integer := 1;

  function f return integer is
    constant tmp : integer := 2;
  begin
    return tmp;
  end function f;

end package body pkg;

architecture rtl of e is

  constant arch : integer := 1;

begin
end architecture rtl;
