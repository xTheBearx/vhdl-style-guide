-- File: top.vhd
-- Function: the top level of the counter example
-- Author: mhsg tests
-- Date: 2026-11-08
-- REQ: HWR-210

library ieee;
  use ieee.std_logic_1164.all;

-- REQ: HWR-211
entity top is
  port (
    clk_i   : in    std_logic;                    -- Clock
    rst_i   : in    std_logic;                    -- Reset
    count_o : out   std_logic_vector(7 downto 0)  -- Count
  );
end entity top;

architecture rtl of top is

begin

  u_counter : entity work.counter(rtl)
    generic map (
      WIDTH => 8                 -- Byte wide
    )
    port map (
      clk_i   => clk_i,          -- Clock
      rst_i   => rst_i,          -- Reset
      en_i    => '1',            -- Always counting
      count_o => count_o         -- Count
    );

  report_label : assert true report "top elaborated" severity note;

end architecture rtl;
