
entity b is
  port (
    aBc  : in    std_logic;
    Data : in    std_logic;
    DeF  : out   std_logic
  );
end entity b;

architecture a of b is

  function f return integer;

  impure function bar (data : std_logic) return std_logic is
    variable abc_local : std_logic;
  begin
    return data and ABC;
  end function bar;

  procedure p is
  begin
    null;
  end procedure p;

begin

  def <= ABC;

  with ABC select def <=
    data when '1',
    '1' when others;

end architecture a;
