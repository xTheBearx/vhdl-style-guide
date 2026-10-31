
architecture a of b is

  subtype my_type is std_logic_vector(7 downto 0);

  function my_func (x : integer) return integer;

begin

  x <= std_logic_vector(y);
  x <= my_type(y);
  z <= my_func(x) when unsigned(x) > 3 else to_integer(signed(x));
  q <= x(3);

  -- Violations below

  x <= STD_LOGIC_VECTOR(y);
  z <= my_func(x) when UNSIGNED(x) > 3 else to_integer(Signed(x));

  u1 : entity work.sub port map (a => Std_Logic_Vector(y), b => to_integer(UNSIGNED(x)));

  process begin
    v := Natural(w);
    p := T_PROJECT(w);
  end process;

end architecture a;
