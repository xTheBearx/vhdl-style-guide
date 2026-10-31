
architecture rtl of e is
begin
  GEN_LABEL : for I in t_index_range generate
    x(i) <= y(I);
    INNER : for i in 0 to 1 generate
      z(i) <= '1';
    end generate INNER;
    w(i) <= '0';
  end generate GEN_LABEL;
  process begin
    for J in 0 to 3 loop
      z(j) <= '0';
      for k in 0 to 1 loop
        q(J, k) <= "i";
      end loop;
    end loop;
    wait;
  end process;
end architecture rtl;
