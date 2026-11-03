library ieee;
use ieee.std_logic_1164.all;

entity md_source is
  port (
    a : in  std_logic;
    y : out std_logic
  );
end entity md_source;

architecture rtl of md_source is
begin

  y <= a;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity md_top is
  port (
    a   : in    std_logic;
    b   : in    std_logic;
    oe  : in    std_logic;
    pin : inout std_logic;
    q   : out   std_logic
  );
end entity md_top;

architecture rtl of md_top is

  signal shared_net : std_logic;

begin

  u_first : entity work.md_source
    port map (
      a => a,
      y => shared_net
    );

  u_second : entity work.md_source
    port map (
      a => b,
      y => shared_net
    );

  q <= shared_net;

  -- A bidirectional pin is not reported
  pin <= a when oe = '1' else 'Z';

end architecture rtl;
