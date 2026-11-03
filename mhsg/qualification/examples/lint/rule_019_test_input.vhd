
entity top is
  port (
    count : buffer unsigned(3 downto 0);
    pad   : inout std_logic;
    a     : in    std_logic
  );
end entity top;

architecture rtl of top is

  procedure swap (x : inout integer) is
  begin
  end procedure swap;

begin

end architecture rtl;
