
architecture rtl of top is

  component usable_vhd is
    port (
      in1  : in    std_logic;
      in2  : in    std_logic_vector(7 downto 0);
      bus1 : inout std_logic;
      out1 : out   std_logic;
      out2 : out   std_logic
    );
  end component usable_vhd;

begin

  u_good : usable_vhd
    port map (
      in1  => d,
      in2  => addr,
      bus1 => b,
      out1 => q1,
      out2 => q2
    );

  u_bad : usable_vhd
    port map (
      in1  => d,
      bus1 => open,
      out1 => open,
      out2 => q
    );

  u_positional : usable_vhd
    port map (d, addr, b, q1);

  u_unknown : entity work.unknown
    port map (
      a => b
    );

end architecture rtl;
