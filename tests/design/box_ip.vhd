library ieee;
use ieee.std_logic_1164.all;

-- A memory controller and a transceiver whose names the IP tools choose. Data read in the user clock of the
-- controller and in the recovered clock of the transceiver is in their domains; data from the system clock is not
entity box_ip_top is
  port (
    sys_clk  : in    std_logic;
    ref_clk  : in    std_logic;
    mem_clk  : in    std_logic;
    rst      : in    std_logic;
    d        : in    std_logic;
    q_mem    : out   std_logic;
    q_rx     : out   std_logic;
    ddr_dq   : inout std_logic;
    rx_p     : in    std_logic;
    tx_p     : out   std_logic
  );
end entity box_ip_top;

architecture rtl of box_ip_top is

  component ddr_ctrl is
    port (
      sys_clk_i       : in    std_logic;
      sys_rst         : in    std_logic;
      ui_clk          : out   std_logic;
      ui_clk_sync_rst : out   std_logic;
      app_wdf_data    : in    std_logic;
      app_rd_data     : out   std_logic;
      init_done       : out   std_logic;
      ddr3_dq         : inout std_logic
    );
  end component;

  component serdes_phy is
    port (
      pll_refclk        : in    std_logic;
      tx_coreclkin      : in    std_logic;
      tx_parallel_data  : in    std_logic;
      tx_clkout         : out   std_logic;
      rx_clkout         : out   std_logic;
      rx_parallel_data  : out   std_logic;
      rx_is_lockedtodata : out  std_logic;
      rx_serial_data    : in    std_logic;
      tx_serial_data    : out   std_logic
    );
  end component;

  signal ui_clk   : std_logic;
  signal ui_rst   : std_logic;
  signal sys_d    : std_logic;
  signal rd_data  : std_logic;
  signal rd_r     : std_logic;
  signal tx_clk   : std_logic;
  signal rx_clk   : std_logic;
  signal rx_data  : std_logic;
  signal rx_r     : std_logic;
  signal rx_bad   : std_logic;

begin

  process (sys_clk) is
  begin
    if rising_edge(sys_clk) then
      sys_d <= d;
    end if;
  end process;

  u_ddr : component ddr_ctrl
    port map (
      sys_clk_i       => mem_clk,
      sys_rst         => rst,
      ui_clk          => ui_clk,
      ui_clk_sync_rst => ui_rst,
      app_wdf_data    => sys_d,
      app_rd_data     => rd_data,
      init_done       => open,
      ddr3_dq         => ddr_dq
    );

  process (ui_clk) is
  begin
    if rising_edge(ui_clk) then
      if ui_rst = '1' then
        rd_r <= '0';
      else
        rd_r <= rd_data;
      end if;
    end if;
  end process;

  u_phy : component serdes_phy
    port map (
      pll_refclk         => ref_clk,
      tx_coreclkin       => tx_clk,
      tx_parallel_data   => sys_d,
      tx_clkout          => tx_clk,
      rx_clkout          => rx_clk,
      rx_parallel_data   => rx_data,
      rx_is_lockedtodata => open,
      rx_serial_data     => rx_p,
      tx_serial_data     => tx_p
    );

  process (rx_clk) is
  begin
    if rising_edge(rx_clk) then
      rx_r <= rx_data;
    end if;
  end process;

  process (sys_clk) is
  begin
    if rising_edge(sys_clk) then
      rx_bad <= rx_data;
    end if;
  end process;

  q_mem <= rd_r;
  q_rx  <= rx_r xor rx_bad;

end architecture rtl;
