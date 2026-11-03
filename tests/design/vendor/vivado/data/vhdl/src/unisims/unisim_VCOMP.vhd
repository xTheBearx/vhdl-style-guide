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

  attribute BOX_TYPE : string;
  attribute BOX_TYPE of BUFG : component is "PRIMITIVE";

end package vcomponents;
