
entity e is
  generic (
    g_width : integer := 1
  );
  port (
    a : in    std_logic;
    b : out   integer -- comment
  );
end entity e;

architecture rtl of e is

  component c is
    port (
      a : in    std_logic
    );
  end component c;

  procedure p (
    x : in    integer;
    y : out   integer
  ) is
  begin
  end procedure p;

  function f (x : integer) return integer;

  impure function g return integer;

begin
end architecture rtl;
