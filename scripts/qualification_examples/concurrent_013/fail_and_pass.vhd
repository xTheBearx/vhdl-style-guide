-- Qualification example of concurrent_013: the first concurrent assignment has no label, the second has one

architecture rtl of gate is
begin

  y <= a and b;
  z_assign : z <= a or b;

end architecture rtl;
