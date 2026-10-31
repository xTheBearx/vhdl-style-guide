
architecture rtl of e is
  constant MARKER_RX : std_logic_vector(31 downto 0) :=
  EXPECT_MARKER(7 downto 0) & EXPECT_MARKER(15 downto 8);
  constant SHORT_C : std_logic_vector(3 downto 0) := A(1 downto 0) &
  A(3 downto 2);
begin
  rd_addr(RD_FETCH * RX_ADDR_W + RX_ADDR_W - 1 downto RD_FETCH * RX_ADDR_W) <=
  lf_bank & std_logic_vector(to_unsigned(lf_rd_off, 5));
  x <= a and
  b;
end architecture rtl;
