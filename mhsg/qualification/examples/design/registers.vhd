library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity registers_top is
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    start : in  std_logic;
    d     : in  std_logic;
    busy  : out std_logic;
    ready : out std_logic;
    q     : out std_logic;
    u     : out std_logic
  );
end entity registers_top;

architecture rtl of registers_top is

  signal busy_r  : std_logic;
  signal ready_r : std_logic;
  signal count   : unsigned(7 downto 0);
  signal q_r     : std_logic;
  signal missing : std_logic;

begin

  proc_regs : process (clk, rst) is
  begin
    if rst = '1' then
      busy_r  <= '0';
      ready_r <= '0';
      count   <= (others => '0');
      q_r     <= '0';
    elsif rising_edge(clk) then
      -- Never changes: assigned only its reset value
      busy_r <= '0';
      -- Changes once after reset: not reported
      ready_r <= '1';
      -- Never read
      count <= count + 1;
      if start = '1' then
        q_r <= d;
      end if;
    end if;
  end process proc_regs;

  busy  <= busy_r;
  ready <= ready_r;
  q     <= q_r;
  u     <= missing;

end architecture rtl;
