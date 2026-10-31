
entity top is
end entity top;

architecture rtl of top is

  component comp is
    port (
      a : in  std_logic;
      z : out std_logic
    );
  end component comp;

begin

  u_sub : entity work.sub
    port map (
      q       => s_q, -- result
      data(1) => d1,
      data(0) => d0,
      clk     => clk
    );

  u_comp : comp port map (z => s_z, a => s_a);

  u_conv : entity work.sub
    port map (
      to_slv(q) => s_q,
      clk       => clk,
      data      => d
    );

  u_positional : entity work.sub port map (clk, d, s_q);

  u_unknown : entity work.unknown port map (b => x, a => y);

end architecture rtl;
