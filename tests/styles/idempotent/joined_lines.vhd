-- When a fix joins two lines or moves the first token of a line, the old
-- indent must not stay in the line until the next fix (issue #79).

architecture a of e is

  signal om : t_vec(1 downto 0) := (others => (
      valid_bit => '0')
    );

begin
end architecture a;

package p is

  type tDivProps is
    record  -- Properties
      steps : integer;
    end record;

end package p;

package p is

	type tDivProps is
		record	-- Properties
			steps : integer;	-- Steps
		end record;

end package p;

architecture a of e is
begin

  process is
  begin

    simAssertion(((dval = 0) and (zz = 1)) or
					 ((dval /= 0) and
					  (to_integer(qq) = aval)),
					 "INST");

  end process;

end architecture a;
