
architecture rtl of top is

  component child is
    port (
      i : in  std_logic;
      o : out std_logic
    );
  end component child;

begin

  operate_proc : process (a1) is
  begin
    a3 <= a1;
    vec(0) <= a1;
    rec.a <= a1;
  end process;

  test_proc : process (a2) is
  begin
    a3 <= a2;
    vec(1) <= a2;
    rec.b <= a2;
    mem(addr) <= a2;
  end process;

  mem(addr2) <= a1;
  q <= a1;

  u_child : child
    port map (
      i => a1,
      o => q
    );

end architecture rtl;
