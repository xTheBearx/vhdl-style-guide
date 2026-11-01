
architecture rtl of fifo is

  constant c_rec : t_rec := (enable => '1', data => x"00");
  constant c_bad : t_rec := (enable => '1', data => x"00");
  constant c_aligned : t_rec := (
    enable     => '1',
    data       => x"00"
  );

begin

  a <= (others => '0');
  a <= (others=> '0');
  a <= (enable => '1', data =>x"00");
  a <= (1 => '1', 2 | 3 => '0');

  process is
  begin

    result := get(arr => data, idx => 1);
    result := get(arr => data, idx => 1);

  end process;

end architecture rtl;
