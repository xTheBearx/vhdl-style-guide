library ieee;
use ieee.std_logic_1164.all;

-- A two-register synchronizer in VHDL, used by the Verilog top of vtop.v

entity vtop_sync is
  port (
    clk : in  std_logic;
    d   : in  std_logic;
    q   : out std_logic
  );
end entity vtop_sync;

architecture rtl of vtop_sync is

  signal meta : std_logic;

begin

  proc_sync : process (clk) is
  begin
    if rising_edge(clk) then
      meta <= d;
      q    <= meta;
    end if;
  end process proc_sync;

end architecture rtl;
