
entity e is
  port (
    a : in    std_logic_vector(7 downto 0);
    b : in    std_logic_vector(0 to 7)
  );
end entity e;

architecture rtl of e is
  type memory_t is array (0 to 15) of std_logic_vector(7 downto 0);
  signal c : unsigned(0 to 3);
  signal d : unsigned(3 downto 0);
begin
end architecture rtl;
