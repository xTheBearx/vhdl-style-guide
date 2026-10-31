
architecture rtl of e is
begin
  process begin
    start_pkt(x"3", CMD, x"2", x"00000030",
      extras => (0 => x"0000000A", 1 => x"0000000B",
        others => (others => '0')), n_ex => 3);
    proc(a => 1, bb => 2,
      ccc => 3,
      d => 4);
  end process;
end architecture rtl;
