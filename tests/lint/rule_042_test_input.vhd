
architecture rtl of counter is
begin
  -- Wraps around at its maximum
  count <= count + 1 when rising_edge(clk);
  other <= count;
  third <= other;
end architecture rtl;
