
architecture a of b is

  subtype my_type is std_logic_vector(7 downto 0);

  function my_func (x : integer) return integer;

begin

  x <= std_logic_vector(y);
  x <= my_type(y);
  z <= my_func(x) when unsigned(x) > 3 else to_integer(signed(x));
  q <= x(3);

  -- Violations below

  x <= std_logic_vector(y);
  z <= my_func(x) when unsigned(x) > 3 else to_integer(signed(x));

  u1 : entity work.sub port map (a => std_logic_vector(y), b => to_integer(unsigned(x)));

  process begin
    v := natural(w);
    p := t_project(w);
  end process;

end architecture a;
