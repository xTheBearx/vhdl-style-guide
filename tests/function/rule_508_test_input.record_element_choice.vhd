
package body p is

  type t is record
    PARAM : std_logic;
  end record;

  function f (param : std_logic; idx : natural) return t is
    variable r : t;
    variable v : std_logic_vector(3 downto 0);
  begin
    r := (PARAM => PARAM);
    v := (IDX => '1', others => '0');
    return r;
  end function;

end package body;
