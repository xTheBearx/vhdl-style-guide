
architecture rtl of top is

  signal   r_sig   : real;
  constant C_RATIO : real := 1.5;
  shared variable count : integer;
  type ptr_t is access integer;
  file log_file : text;

begin

  q <= d after 1 ns;
  w <= transport d after 2 ns;

  process is
  begin
    wait until rising_edge(clk);
    a <= b;
  end process;

end architecture rtl;
