
architecture rtl of fifo is

  signal a, b, c, sel : std_logic;
  constant C_WIDTH : integer := 4;

begin

  proc_good : process (a, b, sel) is
    variable v : std_logic;
  begin
    v := a;
    if sel = '1' then
      c <= v and b and C_WIDTH > 2;
    else
      c <= '0';
    end if;
  end process;

  proc_missing_extra : process (a, c) is
  begin
    if sel = '1' then
      b <= a;
    else
      b <= '0';
    end if;
  end process;

  proc_clocked : process (clk, a) is
  begin
    if rst = '1' then
      b <= '0';
    elsif rising_edge(clk) then
      b <= a;
    end if;
  end process;

  proc_all : process (all) is
  begin
    b <= a;
  end process;

end architecture rtl;
