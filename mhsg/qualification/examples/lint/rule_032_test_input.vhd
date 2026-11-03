
package config_pkg is
  constant c_depth : natural;
  constant c_width : natural;
  constant c_name  : string := "fifo";
end package config_pkg;

package body config_pkg is
  constant c_depth : natural := 16;
end package body config_pkg;

package other_pkg is
  constant c_size : natural;
end package other_pkg;
