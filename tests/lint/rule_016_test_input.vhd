
entity top is
  port (
    count_i : in  natural;
    index_i : in  integer range 0 to 7;
    data_o  : out std_logic
  );
end entity top;

architecture rtl of top is

  signal   count    : natural;
  signal   level    : integer range -4 to 3;
  signal   total    : positive;
  constant C_DEPTH  : natural := 16;

begin

end architecture rtl;
