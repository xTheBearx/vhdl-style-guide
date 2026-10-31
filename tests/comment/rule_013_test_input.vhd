
library ieee;
  use ieee.std_logic_1164.all;

architecture rtl of fifo is

  signal rd_en : std_logic;
  signal empty : std_logic;

begin

  -- Wait for the FIFO to empty
  -- If the FIFO is full then
  -- TODO: fix this then
  -- Note: the write side is in the other process;
  -- Read data;
  --------------------------------------
  -- synthesis translate_off
  -- This is where the reset begins

  process (empty) is
  begin
    if empty = '1' then  -- rd_en <= '1';
      rd_en <= '1';
    end if;
  end process;

  -- Violations below

  -- use ieee.numeric_std.all;
  -- library ieee;
  -- signal full : std_logic;
  -- constant c_depth : integer := 16;
  -- if rd_en = '1' then
  -- rd_en <= '0'; -- old value
  -- end if;
  -- if rising_edge(clk) and rd_en'event then
  -- rd_en <= x"FF";

end architecture rtl;
