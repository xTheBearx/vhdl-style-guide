
architecture rtl of hier_a is

begin

  -- hier_b instantiates hier_sync too, so in a run with hier_b.vhd its ports are not checked
  u_sync : entity work.hier_sync
    port map (
      clk => clk,
      d   => a_i,
      q   => a_o
    );

end architecture rtl;
