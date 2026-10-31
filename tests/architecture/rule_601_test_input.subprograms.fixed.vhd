
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
    return data and aBc;
  end function bar;

  procedure p is
  begin
    null;
  end procedure p;

begin

  DeF <= aBc;

  with aBc select DeF <=
    Data when '1',
    '1' when others;

end architecture a;
