library ieee;
use ieee.std_logic_1164.all;

-- Reset domain crossings: two resets, each released through a reset synchronizer, on one clock

entity rdc_top is
  port (
    clk     : in  std_logic;
    rst_a_n : in  std_logic;
    rst_b_n : in  std_logic;
    d       : in  std_logic;
    q       : out std_logic_vector(3 downto 0)
  );
end entity rdc_top;

architecture rtl of rdc_top is

  signal sync_a  : std_logic_vector(1 downto 0);
  signal sync_b  : std_logic_vector(1 downto 0);
  signal rst_a   : std_logic;
  signal rst_b   : std_logic;
  signal rst_ab  : std_logic;
  signal a_r     : std_logic;
  signal same_r  : std_logic;
  signal other_r : std_logic;
  signal both_r  : std_logic;
  signal free_r  : std_logic;

begin

  proc_sync_a : process (clk, rst_a_n) is
  begin
    if rst_a_n = '0' then
      sync_a <= (others => '1');
    elsif rising_edge(clk) then
      sync_a <= sync_a(0) & '0';
    end if;
  end process proc_sync_a;

  proc_sync_b : process (clk, rst_b_n) is
  begin
    if rst_b_n = '0' then
      sync_b <= (others => '1');
    elsif rising_edge(clk) then
      sync_b <= sync_b(0) & '0';
    end if;
  end process proc_sync_b;

  rst_a  <= sync_a(1);
  rst_b  <= sync_b(1);
  rst_ab <= rst_a or rst_b;

  proc_a : process (clk, rst_a) is
  begin
    if rst_a = '1' then
      a_r    <= '0';
      same_r <= '0';
    elsif rising_edge(clk) then
      a_r    <= d;
      -- The same reset: safe
      same_r <= a_r;
    end if;
  end process proc_a;

  -- Another reset: a reset domain crossing
  proc_other : process (clk, rst_b) is
  begin
    if rst_b = '1' then
      other_r <= '0';
    elsif rising_edge(clk) then
      other_r <= not a_r;
    end if;
  end process proc_other;

  -- A reset that combines both: reset whenever a_r is, so safe
  proc_both : process (clk, rst_ab) is
  begin
    if rst_ab = '1' then
      both_r <= '0';
    elsif rising_edge(clk) then
      both_r <= a_r;
    end if;
  end process proc_both;

  -- No reset: not reported
  proc_free : process (clk) is
  begin
    if rising_edge(clk) then
      free_r <= a_r;
    end if;
  end process proc_free;

  q <= same_r & other_r & both_r & free_r;

end architecture rtl;
