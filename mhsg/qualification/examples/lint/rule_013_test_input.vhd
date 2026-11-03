
entity top is
  port (
    clk   : in  std_logic := '0';
    q     : out std_logic := '0';
    q2    : out std_logic
  );
end entity top;

architecture rtl of top is

  signal count    : unsigned(3 downto 0) := (others => '0');
  signal a, b     : std_logic := '0';
  signal c        : std_logic;
  constant C_ZERO : std_logic := '0';

begin

end architecture rtl;
