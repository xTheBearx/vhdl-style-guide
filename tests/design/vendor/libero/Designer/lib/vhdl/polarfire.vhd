-- A small stand-in for a vendor declaration package, written for tests
library ieee;
use ieee.std_logic_1164.all;

package components is

  component CLKINT is
    port (
      Y : out std_logic;
      A : in  std_logic
    );
  end component;

  component GCLKINT is
    port (
      Y  : out std_logic;
      A  : in  std_logic;
      EN : in  std_logic
    );
  end component;

  component SLE is
    port (
      Q   : out std_logic;
      D   : in  std_logic;
      CLK : in  std_logic;
      EN  : in  std_logic;
      ALn : in  std_logic;
      ADn : in  std_logic;
      SLn : in  std_logic;
      SD  : in  std_logic;
      LAT : in  std_logic
    );
  end component;

  component RAM1K20 is
    port (
      A_DOUT  : out std_logic_vector(7 downto 0);
      B_DOUT  : out std_logic_vector(7 downto 0);
      A_CLK   : in  std_logic;
      A_ADDR  : in  std_logic_vector(3 downto 0);
      A_DIN   : in  std_logic_vector(7 downto 0);
      A_WEN   : in  std_logic;
      A_ARST_N : in std_logic;
      B_CLK   : in  std_logic;
      B_ADDR  : in  std_logic_vector(3 downto 0);
      B_DIN   : in  std_logic_vector(7 downto 0);
      B_WEN   : in  std_logic;
      B_ARST_N : in std_logic
    );
  end component;

end package components;
