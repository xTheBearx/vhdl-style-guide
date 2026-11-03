-- A small stand-in for a vendor declaration package, written for tests
library ieee;
use ieee.std_logic_1164.all;

package vcomponents is

  component BUFG is
    port (
      O : out std_ulogic;
      I : in  std_ulogic
    );
  end component;

  component IBUF is
    generic (
      IOSTANDARD : string := "DEFAULT"
    );
    port (
      O : out std_ulogic;
      I : in  std_ulogic
    );
  end component;

  component BUFGMUX is
    port (
      O  : out std_ulogic;
      I0 : in  std_ulogic;
      I1 : in  std_ulogic;
      S  : in  std_ulogic
    );
  end component;

  component MMCME2_BASE is
    generic (
      CLKFBOUT_MULT_F  : real    := 5.0;
      CLKOUT0_DIVIDE_F : real    := 1.0;
      CLKOUT1_DIVIDE   : integer := 1
    );
    port (
      CLKFBOUT : out std_ulogic;
      CLKOUT0  : out std_ulogic;
      CLKOUT1  : out std_ulogic;
      LOCKED   : out std_ulogic;
      CLKFBIN  : in  std_ulogic;
      CLKIN1   : in  std_ulogic;
      PWRDWN   : in  std_ulogic;
      RST      : in  std_ulogic
    );
  end component;

  attribute BOX_TYPE : string;
  attribute BOX_TYPE of BUFG : component is "PRIMITIVE";

end package vcomponents;
