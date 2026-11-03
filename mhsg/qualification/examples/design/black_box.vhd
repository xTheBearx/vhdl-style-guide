library ieee;
use ieee.std_logic_1164.all;

-- Vendor primitives declared as components without entities: GHDL keeps them as black boxes

entity bb_top is
  port (
    clk_in : in  std_logic;
    ce     : in  std_logic;
    d      : in  std_logic;
    clk_b  : in  std_logic;
    q      : out std_logic;
    s      : out std_logic
  );
end entity bb_top;

architecture rtl of bb_top is
  component BUFGCE is
    port (
      O  : out std_logic;
      CE : in  std_logic;
      I  : in  std_logic
    );
  end component;
  component xpm_cdc_single is
    generic (
      DEST_SYNC_FF  : integer := 4;
      SRC_INPUT_REG : integer := 1
    );
    port (
      src_clk  : in  std_logic;
      src_in   : in  std_logic;
      dest_clk : in  std_logic;
      dest_out : out std_logic
    );
  end component;
  signal clk : std_logic;
  signal r   : std_logic;
begin

  u_buf : BUFGCE
    port map (
      O  => clk,
      CE => ce,
      I  => clk_in
    );

  proc_r : process (clk) is
  begin
    if rising_edge(clk) then
      r <= d;
    end if;
  end process proc_r;

  q <= r;

  u_sync : xpm_cdc_single
    generic map (
      DEST_SYNC_FF  => 3,
      SRC_INPUT_REG => 0
    )
    port map (
      src_clk  => clk,
      src_in   => r,
      dest_clk => clk_b,
      dest_out => s
    );

end architecture rtl;
