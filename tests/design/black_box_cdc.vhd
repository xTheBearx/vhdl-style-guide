library ieee;
use ieee.std_logic_1164.all;

-- Black boxes whose clock domain behaviour is declared in black_box_cdc.yaml

entity bbc_top is
  port (
    clk_pad : in  std_logic;
    clk_b   : in  std_logic;
    d       : in  std_logic_vector(3 downto 0);
    q       : out std_logic_vector(7 downto 0)
  );
end entity bbc_top;

architecture rtl of bbc_top is

  component IBUF is
    port (
      O : out std_logic;
      I : in  std_logic
    );
  end component;

  component BUFG is
    port (
      O : out std_logic;
      I : in  std_logic
    );
  end component;

  component clock_gen is
    port (
      clk_in   : in  std_logic;
      clk_out0 : out std_logic;
      clk_out1 : out std_logic;
      locked   : out std_logic
    );
  end component;

  component cdc_bit is
    generic (
      STAGES : integer := 2
    );
    port (
      src_clk  : in  std_logic;
      src_in   : in  std_logic;
      dest_clk : in  std_logic;
      dest_out : out std_logic
    );
  end component;

  component dual_ip is
    port (
      aclk   : in  std_logic;
      bclk   : in  std_logic;
      a_data : in  std_logic;
      b_data : out std_logic;
      cfg    : in  std_logic;
      irq    : out std_logic
    );
  end component;

  component mystery is
    port (
      x : in  std_logic;
      y : out std_logic
    );
  end component;

  signal clk_ibuf : std_logic;
  signal clk      : std_logic;
  signal clk0     : std_logic;
  signal clk1     : std_logic;
  signal locked   : std_logic;
  signal flag_a   : std_logic;
  signal mode_a   : std_logic;
  signal flag_b   : std_logic;
  signal mode_b   : std_logic;
  signal both_b   : std_logic;
  signal reg0     : std_logic;
  signal reg1     : std_logic;
  signal bdata_b  : std_logic;
  signal b_out    : std_logic;
  signal irq      : std_logic;
  signal irq_q    : std_logic;
  signal locked_q : std_logic;
  signal y        : std_logic;

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

  u_gen : clock_gen
    port map (
      clk_in   => clk,
      clk_out0 => clk0,
      clk_out1 => clk1,
      locked   => locked
    );

  proc_a : process (clk) is
  begin
    if rising_edge(clk) then
      flag_a <= d(0);
      mode_a <= d(1);
      irq_q  <= irq;
    end if;
  end process proc_a;

  -- Two vendor synchronizers whose outputs meet again
  u_sync_flag : cdc_bit
    generic map (
      STAGES => 3
    )
    port map (
      src_clk  => clk,
      src_in   => flag_a,
      dest_clk => clk_b,
      dest_out => flag_b
    );

  u_sync_mode : cdc_bit
    generic map (
      STAGES => 3
    )
    port map (
      src_clk  => clk,
      src_in   => mode_a,
      dest_clk => clk_b,
      dest_out => mode_b
    );

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      both_b  <= flag_b and mode_b;
      bdata_b <= d(2);
    end if;
  end process proc_b;

  -- clk0 is derived from clk: no crossing; clk1 is independent: a crossing
  proc_gen : process (clk0) is
  begin
    if rising_edge(clk0) then
      reg0 <= flag_a;
    end if;
  end process proc_gen;

  proc_ind : process (clk1) is
  begin
    if rising_edge(clk1) then
      reg1 <= flag_a;
    end if;
  end process proc_ind;

  -- a_data is timed by aclk, which is clk, but driven from clk_b
  u_ip : dual_ip
    port map (
      aclk   => clk,
      bclk   => clk_b,
      a_data => bdata_b,
      b_data => b_out,
      cfg    => d(3),
      irq    => irq
    );

  -- The lock output of the clock generator, an asynchronous output, used as an asynchronous reset
  proc_locked : process (clk, locked) is
  begin
    if locked = '0' then
      locked_q <= '0';
    elsif rising_edge(clk) then
      locked_q <= d(3);
    end if;
  end process proc_locked;

  u_mystery : mystery
    port map (
      x => d(0),
      y => y
    );

  q <= both_b & reg0 & reg1 & b_out & irq_q & locked_q & y & '0';

end architecture rtl;
