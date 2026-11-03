-- A small stand-in for a vendor declaration package, written for tests
library ieee;
use ieee.std_logic_1164.all;

package vcomponents is

  component xpm_cdc_single is
    generic (
      DEST_SYNC_FF   : integer := 4;
      INIT_SYNC_FF   : integer := 0;
      SIM_ASSERT_CHK : integer := 0;
      SRC_INPUT_REG  : integer := 1
    );
    port (
      dest_out : out std_logic;
      dest_clk : in  std_logic;
      src_clk  : in  std_logic;
      src_in   : in  std_logic
    );
  end component;

end package vcomponents;
