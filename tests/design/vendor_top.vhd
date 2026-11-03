library ieee;
use ieee.std_logic_1164.all;

library unisim;
use unisim.vcomponents.all;

library xpm;
use xpm.vcomponents.all;

entity vendor_top is
  port (
    clk_pad : in  std_logic;
    clk_b   : in  std_logic;
    d       : in  std_logic;
    q       : out std_logic
  );
end entity vendor_top;

architecture rtl of vendor_top is

  signal clk_ibuf : std_logic;
  signal clk      : std_logic;
  signal r        : std_logic;

begin

  u_ibuf : IBUF
    generic map (
      IOSTANDARD => "LVCMOS33"
    )
    port map (
      O => clk_ibuf,
      I => clk_pad
    );

  u_bufg : BUFG
    port map (
      O => clk,
      I => clk_ibuf
    );

  proc_r : process (clk) is
  begin
    if rising_edge(clk) then
      r <= d;
    end if;
  end process proc_r;

  u_sync : xpm_cdc_single
    generic map (
      DEST_SYNC_FF => 3
    )
    port map (
      dest_out => q,
      dest_clk => clk_b,
      src_clk  => clk,
      src_in   => r
    );

end architecture rtl;
