
package pkg is

  constant c_width : integer := 8;
  constant c_max   : integer := C_WIDTH * 2;

end package pkg;

package body pkg is

  constant c_local : integer := C_Width + c_max;

  function f (a : integer) return integer is
    constant c_width : integer := 4;
  begin
    -- c_width here is the local constant, which hides the package constant
    return C_WIDTH + C_MAX + C_LOCAL;
  end function f;

end package body pkg;

package other is

  -- c_width is not declared in this package
  constant c_size : integer := C_WIDTH;

end package other;
