
-- REQ: HWR-1
entity top is
end entity top;

-- Counter
entity other is
end entity other;

architecture rtl of top is

begin

  -- Output register
  -- REQ: HWR-2
  proc_out : process (clk) is
  begin
  end process proc_out;

  proc_in : process (clk) is
  begin
  end process proc_in;

end architecture rtl;
