library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity reach_top is
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    go    : in  std_logic;
    alarm : out std_logic;
    half  : out std_logic
  );
end entity reach_top;

architecture rtl of reach_top is
  signal count : unsigned(2 downto 0);
begin
  process (clk, rst) is
  begin
    if rst = '1' then
      count <= (others => '0');
      alarm <= '0';
      half  <= '0';
    elsif rising_edge(clk) then
      if go = '1' then
        if count = 5 then
          count <= (others => '0');
        else
          count <= count + 1;
        end if;
      end if;
      -- count never reaches 7
      if count = 7 then
        alarm <= '1';
      end if;
      if count = 3 then
        half <= '1';
      end if;
    end if;
  end process;
end architecture rtl;
