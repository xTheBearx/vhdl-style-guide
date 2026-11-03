library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.all;

library xpm;
use xpm.vcomponents.all;

-- Xilinx primitives and XPM macros declared by the xilinx library of mhsg

entity xilinx_top is
  port (
    clk_pad : in  std_logic;
    clk_b   : in  std_logic;
    sel     : in  std_logic;
    d       : in  std_logic_vector(7 downto 0);
    q       : out std_logic_vector(31 downto 0)
  );
end entity xilinx_top;

architecture rtl of xilinx_top is

  signal clk_ibuf  : std_logic;
  signal clk       : std_logic;
  signal clk_fb    : std_logic;
  signal clk0      : std_logic;
  signal clk1      : std_logic;
  signal locked    : std_logic;
  signal clk_mux   : std_logic;
  signal count_a   : unsigned(3 downto 0);
  signal en_a      : std_logic;
  signal flag_a    : std_logic;
  signal fast_q    : std_logic;
  signal mux_q     : std_logic;
  signal gray_b    : std_logic_vector(3 downto 0);
  signal fifo_out  : std_logic_vector(7 downto 0);
  signal empty     : std_logic;
  signal full      : std_logic;
  signal ram_out_a : std_logic_vector(7 downto 0);
  signal ram_out_b : std_logic_vector(7 downto 0);
  signal ind_out_a : std_logic_vector(7 downto 0);
  signal ind_out_b : std_logic_vector(7 downto 0);

begin

  u_ibuf : IBUF
    port map (
      O => clk_ibuf,
      I => clk_pad
    );

  u_bufg : BUFG
    port map (
      O => clk,
      I => clk_ibuf
    );

  u_mmcm : MMCME2_BASE
    port map (
      CLKFBOUT => clk_fb,
      CLKOUT0  => clk0,
      CLKOUT1  => clk1,
      LOCKED   => locked,
      CLKFBIN  => clk_fb,
      CLKIN1   => clk,
      PWRDWN   => '0',
      RST      => '0'
    );

  u_mux : BUFGMUX
    port map (
      O  => clk_mux,
      I0 => clk,
      I1 => clk_b,
      S  => sel
    );

  proc_a : process (clk) is
  begin
    if rising_edge(clk) then
      count_a <= count_a + 1;
      en_a    <= d(0);
      flag_a  <= d(1);
    end if;
  end process proc_a;

  -- A clock of the MMCM is derived from clk: no crossing
  proc_fast : process (clk0) is
  begin
    if rising_edge(clk0) then
      fast_q <= flag_a;
    end if;
  end process proc_fast;

  -- The output of the clock multiplexer is a clock of its own: a crossing
  proc_mux : process (clk_mux) is
  begin
    if rising_edge(clk_mux) then
      mux_q <= flag_a;
    end if;
  end process proc_mux;

  u_gray : xpm_cdc_gray
    generic map (
      DEST_SYNC_FF => 3,
      WIDTH        => 4
    )
    port map (
      dest_out_bin => gray_b,
      dest_clk     => clk_b,
      src_clk      => clk,
      src_in_bin   => std_logic_vector(count_a)
    );

  -- rd_en is timed by rd_clk, clk_b, but driven from clk: a crossing
  u_fifo : xpm_fifo_async
    generic map (
      WRITE_DATA_WIDTH => 8,
      READ_DATA_WIDTH  => 8
    )
    port map (
      dout   => fifo_out,
      empty  => empty,
      full   => full,
      din    => d,
      rd_clk => clk_b,
      rd_en  => en_a,
      rst    => '0',
      sleep  => '0',
      wr_clk => clk,
      wr_en  => en_a
    );

  -- With a common clock, port b is timed by clka: no crossing
  u_ram_common : xpm_memory_tdpram
    generic map (
      CLOCKING_MODE => "common_clock"
    )
    port map (
      douta => ram_out_a,
      doutb => ram_out_b,
      addra => std_logic_vector(count_a),
      addrb => std_logic_vector(count_a),
      clka  => clk,
      clkb  => clk_b,
      dina  => d,
      dinb  => d,
      ena   => '1',
      enb   => '1',
      sleep => '0',
      wea   => "0",
      web   => "0"
    );

  -- With independent clocks, port b is timed by clkb: addrb crosses
  u_ram_independent : xpm_memory_tdpram
    generic map (
      CLOCKING_MODE => "independent_clock"
    )
    port map (
      douta => ind_out_a,
      doutb => ind_out_b,
      addra => std_logic_vector(count_a),
      addrb => std_logic_vector(count_a),
      clka  => clk,
      clkb  => clk_b,
      dina  => d,
      dinb  => d,
      ena   => '1',
      enb   => '1',
      sleep => '0',
      wea   => "0",
      web   => "0"
    );

  q <= fast_q & mux_q & locked & clk1 & gray_b & fifo_out & empty & full & ram_out_b(3 downto 0) & ind_out_b(7 downto 0) & '0' & '0';

end architecture rtl;
