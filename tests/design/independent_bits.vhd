-- A vector input whose bits are independent signals, each synchronized by two registers of its own (issue 92), and
-- the same with two of the synchronized bits combined after their synchronizers

library ieee;
  use ieee.std_logic_1164.all;

entity independent_bits_top is
  port (
    clk : in    std_logic;
    d_i : in    std_logic_vector(3 downto 0);
    q_o : out   std_logic_vector(3 downto 0)
  );
end entity independent_bits_top;

architecture rtl of independent_bits_top is

  signal d_meta : std_logic_vector(3 downto 0);
  signal d_sync : std_logic_vector(3 downto 0);

begin

  proc_sync : process (clk) is
  begin
    if rising_edge(clk) then
      d_meta <= d_i;
      d_sync <= d_meta;
    end if;
  end process proc_sync;

  q_o <= d_sync;

end architecture rtl;

library ieee;
  use ieee.std_logic_1164.all;

entity independent_bits_and_top is
  port (
    clk    : in    std_logic;
    d_i    : in    std_logic_vector(1 downto 0);
    both_o : out   std_logic
  );
end entity independent_bits_and_top;

architecture rtl of independent_bits_and_top is

  signal d_meta : std_logic_vector(1 downto 0);
  signal d_sync : std_logic_vector(1 downto 0);
  signal both_r : std_logic;

begin

  proc_sync : process (clk) is
  begin
    if rising_edge(clk) then
      d_meta <= d_i;
      d_sync <= d_meta;
      both_r <= d_sync(0) and d_sync(1);
    end if;
  end process proc_sync;

  both_o <= both_r;

end architecture rtl;
