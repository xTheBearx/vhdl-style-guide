
architecture rtl of top is

begin

  process (clk) is
    variable count : natural range 0 to 15;
    variable temp  : std_logic;
  begin
    if rising_edge(clk) then
      count := count + 1;
      temp  := a and b;
      q     <= temp;
    end if;
  end process;

end architecture rtl;
