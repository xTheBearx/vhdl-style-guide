
package pkg is

  constant width : integer := 8;

end package pkg;

entity e is
  port (
    data : in std_logic
  );
end entity e;

architecture rtl of e is

  type t_rec is record
    valid : std_logic;
  end record t_rec;

  constant const_depth : integer := 16;
  signal   valid       : std_logic;
  signal   rec         : t_rec;
  signal   count       : integer;
  signal   s_count     : integer;

  function f (x : integer) return integer is
    variable valid : integer;
  begin
    valid := x;
    return valid;
  end function f;

begin

  valid <= data;
  rec   <= (valid => valid);
  rec.valid <= valid;

  u1 : entity work.sub
    port map (
      valid => valid
    );

  process is
    variable tmp : integer;
  begin
    tmp := const_depth;
    count <= tmp;
  end process;

end architecture rtl;
