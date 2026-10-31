
package pkg is

  subtype st_byte is std_logic_vector(7 downto 0);
  subtype word is std_logic_vector(15 downto 0);

end package pkg;

package body pkg is

  subtype local is integer range 0 to 3;

  function f return integer is
    subtype tmp is integer range 0 to 1;
  begin
    return 1;
  end function f;

end package body pkg;

architecture rtl of e is

  subtype arch is integer range 0 to 7;

begin
end architecture rtl;
