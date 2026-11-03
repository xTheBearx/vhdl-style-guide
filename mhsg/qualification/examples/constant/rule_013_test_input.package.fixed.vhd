
package pkg is

  constant c_width : integer := 8;
  constant c_max   : integer := c_width * 2;

end package pkg;

package body pkg is

  constant c_local : integer := c_width + c_max;

  function f (a : integer) return integer is
    constant c_width : integer := 4;
  begin
    -- c_width here is the local constant, which hides the package constant
    return c_width + c_max + c_local;
  end function f;

end package body pkg;

package other is

  -- c_width is not declared in this package
  constant c_size : integer := C_WIDTH;

end package other;
