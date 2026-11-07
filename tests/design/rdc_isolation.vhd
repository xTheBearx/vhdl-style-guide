library ieee;
use ieee.std_logic_1164.all;

-- Reset domain crossings isolated by an enable and a gate: two resets, each released through a reset synchronizer, on
-- one clock
entity rdc_isolation_top is
  port (
    clk     : in  std_logic;
    rst_a_n : in  std_logic;
    rst_b_n : in  std_logic;
    isolate : in  std_logic;
    sel     : in  std_logic;
    d       : in  std_logic;
    q       : out std_logic_vector(2 downto 0)
  );
end entity rdc_isolation_top;

architecture rtl of rdc_isolation_top is
  signal sync_a  : std_logic_vector(1 downto 0);
  signal sync_b  : std_logic_vector(1 downto 0);
  signal rst_a   : std_logic;
  signal rst_b   : std_logic;
  signal a_r     : std_logic;
  signal iso_n   : std_logic;
  signal en_r    : std_logic;
  signal gate_r  : std_logic;
  signal plain_r : std_logic;
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

  rst_a <= sync_a(1);
  rst_b <= sync_b(1);

  proc_a : process (clk, rst_a) is
  begin
    if rst_a = '1' then
      a_r <= '0';
    elsif rising_edge(clk) then
      a_r <= d;
    end if;
  end process proc_a;

  -- The isolation, 0 while rst_a is asserted
  proc_b : process (clk, rst_b) is
  begin
    if rst_b = '1' then
      iso_n   <= '0';
      en_r    <= '0';
      gate_r  <= '0';
      plain_r <= '0';
    elsif rising_edge(clk) then
      iso_n <= not isolate;
      -- Isolated by its enable
      if iso_n = '1' then
        en_r <= a_r;
      end if;
      -- Isolated by a gate
      gate_r <= a_r and iso_n;
      -- Not isolated by iso_n: sel would isolate it
      if sel = '1' then
        plain_r <= a_r;
      end if;
    end if;
  end process proc_b;

  q <= en_r & gate_r & plain_r;

end architecture rtl;
