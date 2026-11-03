
architecture rtl of e is
  constant c_command : std_logic_vector(3 downto 0) := "0110";
begin

  command <= "0110";
  mask    <= x"A5";
  zeros   <= "0000";
  ones    <= x"FF";
  bit_one <= '1';
  aggr    <= (others => '0');

end architecture rtl;
