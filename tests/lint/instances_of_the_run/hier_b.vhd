
architecture rtl of hier_b is

begin

  u_sync : entity work.hier_sync
    port map (
      clk => clk,
      d   => b_i,
      q   => b_o
    );

end architecture rtl;
