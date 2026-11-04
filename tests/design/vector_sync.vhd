library ieee;
use ieee.std_logic_1164.all;

-- A synchronizer written as one vector register, as surf's Synchronizer does: each bit is a stage
entity vector_sync is
  port (
    clk_a  : in  std_logic;
    clk_b  : in  std_logic;
    rst_b  : in  std_logic;
    flag_a : in  std_logic;
    flag_b : out std_logic
  );
end entity vector_sync;

architecture rtl of vector_sync is

  signal flag_r : std_logic;
  signal sync_r : std_logic_vector(1 downto 0);

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      flag_r <= flag_a;
    end if;
  end process proc_a;

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      if rst_b = '1' then
        sync_r <= (others => '0');
      else
        sync_r <= sync_r(0) & flag_r;
      end if;
    end if;
  end process proc_b;

  flag_b <= sync_r(1);

end architecture rtl;
