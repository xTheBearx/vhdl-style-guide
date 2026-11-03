
architecture rtl of e is
  signal delay_1 : std_logic;
  signal delay_2 : std_logic;
  signal copy    : std_logic;
begin

  delay_1 <= not trigger;
  delay_2 <= not delay_1;
  copy    <= trigger;
  y       <= a and b;

end architecture rtl;
