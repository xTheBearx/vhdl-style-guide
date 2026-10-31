
architecture rtl of e is
begin
  with my_expression select my_output <=
    c_first         when 1,
    c_second        when 2,
    c_third         when 3,
    (others => '0') when others;
  process begin
    with sel select v :=
      a   when '0',
      bbb when others;
    wait;
  end process;
end architecture rtl;
