
package pkg is

  type t_state is (IDLE, RUN);
  constant c_width : integer := 8;

end package pkg;

package body pkg is

  constant c_local : integer := c_width;

end package body pkg;

entity e is
  generic (
    g_depth : integer := 4
  );
  port (
    clk : in std_logic
  );
end entity e;

architecture rtl of e is

  type t_rec is record
    valid : std_logic;
  end record t_rec;

  signal state : t_state;
  signal valid : std_logic;

  function f (x : integer) return integer is
    variable valid : integer;
  begin
    valid := x;
    return valid;
  end function f;

begin

  proc : process (clk) is
    variable v_count : integer;
  begin
    for i in 0 to g_depth loop
      v_count := i;
    end loop;
  end process proc;

  gen : for j in 0 to 3 generate
    signal s_gen : std_logic;
  begin
    s_gen <= valid;
  end generate gen;

end architecture rtl;
