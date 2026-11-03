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

  component xpm_cdc_gray is
    generic (
      DEST_SYNC_FF : integer := 4;
      WIDTH        : integer := 2
    );
    port (
      dest_out_bin : out std_logic_vector(WIDTH - 1 downto 0);
      dest_clk     : in  std_logic;
      src_clk      : in  std_logic;
      src_in_bin   : in  std_logic_vector(WIDTH - 1 downto 0)
    );
  end component;

  component xpm_fifo_async is
    generic (
      WRITE_DATA_WIDTH : integer := 32;
      READ_DATA_WIDTH  : integer := 32
    );
    port (
      dout   : out std_logic_vector(READ_DATA_WIDTH - 1 downto 0);
      empty  : out std_logic;
      full   : out std_logic;
      din    : in  std_logic_vector(WRITE_DATA_WIDTH - 1 downto 0);
      rd_clk : in  std_logic;
      rd_en  : in  std_logic;
      rst    : in  std_logic;
      sleep  : in  std_logic;
      wr_clk : in  std_logic;
      wr_en  : in  std_logic
    );
  end component;

  component xpm_memory_tdpram is
    generic (
      CLOCKING_MODE : string := "common_clock"
    );
    port (
      douta : out std_logic_vector(7 downto 0);
      doutb : out std_logic_vector(7 downto 0);
      addra : in  std_logic_vector(3 downto 0);
      addrb : in  std_logic_vector(3 downto 0);
      clka  : in  std_logic;
      clkb  : in  std_logic;
      dina  : in  std_logic_vector(7 downto 0);
      dinb  : in  std_logic_vector(7 downto 0);
      ena   : in  std_logic;
      enb   : in  std_logic;
      sleep : in  std_logic;
      wea   : in  std_logic_vector(0 downto 0);
      web   : in  std_logic_vector(0 downto 0)
    );
  end component;

end package vcomponents;
