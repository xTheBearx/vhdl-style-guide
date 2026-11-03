
architecture rtl of e is
begin

  bad_proc : process (all) is
    variable sum : unsigned(7 downto 0);
  begin
    if enable = '1' then
      sum := a + b;
    end if;
    result <= sum;
  end process;

  good_proc : process (all) is
    variable sum : unsigned(7 downto 0);
  begin
    sum := (others => '0');
    if enable = '1' then
      sum := a + b;
    end if;
    result2 <= sum;
  end process;

end architecture rtl;
