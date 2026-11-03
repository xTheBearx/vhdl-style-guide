
architecture rtl of e is
begin

  u_fifo : entity work.fifo
    port map (
      wr_data => payload,
      rd_data => rd_data,
      clk_i   => clk,
      full_o  => s_full,
      empty   => empty_s,
      level   => level_r(3 downto 0)
    );

end architecture rtl;
