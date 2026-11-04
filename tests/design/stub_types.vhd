library ieee;
use ieee.std_logic_1164.all;

library vendorlib;
use vendorlib.components.all;

-- Subtypes, record elements, function calls, aggregates and comments in the maps of a vendor component

package stub_types_pkg is
  subtype sl is std_logic;
  subtype slv is std_logic_vector;
  subtype word is slv(15 downto 0);
  type reg_t is record
    valid : sl;
    data  : word;
  end record reg_t;
  type mode_t is (idle, busy);
end package stub_types_pkg;

library ieee;
use ieee.std_logic_1164.all;

library vendorlib;
use vendorlib.components.all;

use work.stub_types_pkg.all;

entity stub_types_top is
  port (
    clk : in  sl;
    d   : in  word;
    q   : out word;
    v   : out sl
  );
end entity stub_types_top;

architecture rtl of stub_types_top is

  function get_mode return string is
  begin
    return "FAST";
  end function get_mode;

  signal r     : reg_t;
  signal state : mode_t;

begin

  proc_r : process (clk) is
  begin
    if rising_edge(clk) then
      r.valid <= '1';
      r.data  <= d;
    end if;
  end process proc_r;

  u_box : PRIMITIVE
    generic map (
      -- The mode, from a function
      MODE => get_mode
    )
    port map (
      -- The clock
      CLK   => clk,
      DIN   => r.data,
      VALID => r.valid,
      CASIN => (others => '0'),
      STATE => state,
      DOUT  => q,
      READY => v
    );

end architecture rtl;
