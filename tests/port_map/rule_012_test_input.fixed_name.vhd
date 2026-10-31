
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
      clk     => clk,
      data(1) => d1,
      data(0) => d0,
      q       => s_q -- result
    );

  u_comp : comp port map (a => s_a, z => s_z);

  u_conv : entity work.sub
    port map (
      clk       => clk,
      data      => d,
      to_slv(q) => s_q
    );

  u_positional : entity work.sub port map (clk, d, s_q);

  u_unknown : entity work.unknown port map (a => y, b => x);

end architecture rtl;
