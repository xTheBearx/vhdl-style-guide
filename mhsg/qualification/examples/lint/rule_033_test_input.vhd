
architecture rtl of filter is
  signal sum    : unsigned(7 downto 0);
  signal spare  : std_logic;
  signal unused : std_logic;
  signal link   : std_logic;
begin

  sum   <= a + b;
  spare <= a(0);
  y     <= sum;

  u_sub : entity work.sub
    port map (
      q => link
    );

end architecture rtl;
