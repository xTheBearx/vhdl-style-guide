
entity e is
  port (
    clk   : in    std_logic;
    count : out   natural
  );
end entity e;

architecture rtl of e is
  signal busy : std_logic;
begin

  busy : process (clk) is
    variable count : natural;
    variable total : natural;
  begin
    for clk in 0 to 3 loop
      null;
    end loop;
  end process busy;

end architecture rtl;
