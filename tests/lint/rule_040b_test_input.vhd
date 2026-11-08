
architecture rtl of top is

begin

  -- Instantiated once: rst_n is the name of the active low ports, data is the port name, foo is a rename
  u_leaf : entity work.leaf
    port map (
      clk_i   => clk,
      rst_n_i => rst_n,
      rst_ni  => rst_n,
      data_i  => foo,
      tick_o  => tick
    );

  -- Instantiated twice: the instances cannot both connect signals named like the ports
  u_sync_foo : entity work.sync
    port map (
      d_i => foo,
      q_o => foo_s
    );

  u_sync_bar : entity work.sync
    port map (
      d_i => bar,
      q_o => bar_s
    );

  -- Instantiated in a for generate, so more than once
  g_lane : for i in 0 to 1 generate

    u_lane : entity work.lane
      port map (
        d_i => foo
      );

  end generate g_lane;

end architecture rtl;
